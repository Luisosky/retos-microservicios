using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Npgsql;
using ServicioAutenticacion.Data;
using ServicioAutenticacion.Dtos;
using ServicioAutenticacion.Messaging;
using ServicioAutenticacion.Models;
using ServicioAutenticacion.Services;

namespace ServicioAutenticacion.Controllers;

[ApiController]
[Route("auth")]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly AuthDbContext _dbContext;
    private readonly IJwtTokenService _jwtTokenService;
    private readonly IRabbitMqPublisher _publisher;
    private readonly IConfiguration _configuration;
    private readonly ILogger<AuthController> _logger;

    public AuthController(
        AuthDbContext dbContext,
        IJwtTokenService jwtTokenService,
        IRabbitMqPublisher publisher,
        IConfiguration configuration,
        ILogger<AuthController> logger)
    {
        _dbContext = dbContext;
        _jwtTokenService = jwtTokenService;
        _publisher = publisher;
        _configuration = configuration;
        _logger = logger;
    }

    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login([FromBody] LoginRequest request)
    {
        var identifier = request.GetIdentifier();
        if (string.IsNullOrWhiteSpace(identifier))
        {
            return BadRequest(new { message = "Debe enviar usuario o email" });
        }

        var user = await _dbContext.Users
            .AsNoTracking()
            .Where(x => x.Email == identifier)
            .Select(x => new
            {
                x.Email,
                x.Role,
                x.PasswordHash,
                x.IsActive
            })
            .FirstOrDefaultAsync();

        if (user is null || !user.IsActive || string.IsNullOrWhiteSpace(user.PasswordHash)
            || !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
        {
            return Unauthorized(new { message = "Credenciales invalidas" });
        }

        var token = _jwtTokenService.GenerateToken(user.Email, user.Role);
        return Ok(BuildAuthResponse(user.Email, user.Role, token));
    }

    [HttpPost("recover-password")]
    public async Task<IActionResult> RecoverPassword([FromBody] RecoverPasswordRequest request)
    {
        try
        {
            var email = request.Email.Trim().ToLowerInvariant();

            var user = await EnsureRecoverUserAsync(email);

            // Si el empleado fue dado de baja (evento empleado.eliminado lo marca IsActive=false),
            // no se debe permitir generar tokens de recuperación nuevos.
            if (!user.IsActive)
            {
                return Unauthorized(new { mensaje = "La cuenta está deshabilitada." });
            }

            await _dbContext.PasswordResetTokens
                .Where(x => x.UserId == user.Id && !x.IsUsed && x.ExpiresAt > DateTimeOffset.UtcNow)
                .ExecuteUpdateAsync(setters => setters.SetProperty(t => t.IsUsed, true));

            PasswordResetToken recoveryToken = new PasswordResetToken
            {
                Id = Guid.NewGuid(),
                UserId = user.Id,
                Token = Guid.NewGuid().ToString(),
                ExpiresAt = DateTimeOffset.UtcNow.AddMinutes(GetResetTokenExpirationMinutes()),
                IsUsed = false
            };

            // Try inserting the token with a small retry loop in case of rare GUID collision
            const int maxInsertAttempts = 3;
            PasswordResetToken? persistedRecoveryToken = null;
            for (var attempt = 0; attempt < maxInsertAttempts; attempt++)
            {
                var tokenToInsert = new PasswordResetToken
                {
                    Id = Guid.NewGuid(),
                    UserId = user.Id,
                    Token = Guid.NewGuid().ToString(),
                    ExpiresAt = DateTimeOffset.UtcNow.AddMinutes(GetResetTokenExpirationMinutes()),
                    IsUsed = false
                };

                _dbContext.PasswordResetTokens.Add(tokenToInsert);
                var sw = System.Diagnostics.Stopwatch.StartNew();
                try
                {
                    await _dbContext.SaveChangesAsync();
                    sw.Stop();
                    _logger.LogDebug("Saved PasswordResetToken (attempt {Attempt}) in {Elapsed}ms", attempt + 1, sw.ElapsedMilliseconds);
                    persistedRecoveryToken = tokenToInsert;
                    break;
                }
                catch (DbUpdateException ex) when (IsDuplicateConstraint(ex, "auth_reset_tokens_pkey"))
                {
                    sw.Stop();
                    _logger.LogWarning(ex, "Duplicate key on PasswordResetToken insert (attempt {Attempt}). Checking for persisted token.", attempt + 1);
                    _dbContext.Entry(tokenToInsert).State = EntityState.Detached;

                    var persisted = await _dbContext.PasswordResetTokens.AsNoTracking()
                        .FirstOrDefaultAsync(x => x.Token == tokenToInsert.Token);
                    if (persisted is not null)
                    {
                        persistedRecoveryToken = persisted;
                        break;
                    }

                    if (attempt == maxInsertAttempts - 1)
                    {
                        // last attempt failed, rethrow to be handled by outer catch
                        throw;
                    }

                    // small delay to avoid tight loop
                    await Task.Delay(50);
                    continue;
                }
                catch (DbUpdateException ex) when (ex.InnerException is PostgresException pg && pg.SqlState == PostgresErrorCodes.UniqueViolation)
                {
                    sw.Stop();
                    _logger.LogWarning(ex, "Duplicate key on PasswordResetToken insert (attempt {Attempt}). Checking for persisted token.", attempt + 1);
                    _dbContext.Entry(tokenToInsert).State = EntityState.Detached;

                    var persisted = await _dbContext.PasswordResetTokens.AsNoTracking()
                        .FirstOrDefaultAsync(x => x.Token == tokenToInsert.Token);
                    if (persisted is not null)
                    {
                        persistedRecoveryToken = persisted;
                        break;
                    }

                    if (attempt == maxInsertAttempts - 1)
                    {
                        throw;
                    }

                    await Task.Delay(50);
                    continue;
                }
            }

            // Publish event without blocking caller; allow publisher to handle timeouts
            if (persistedRecoveryToken is not null)
            {
                var pubSw = System.Diagnostics.Stopwatch.StartNew();
                await _publisher.PublishAsync("usuario.recuperacion", new
                {
                    id = user.Id,
                    email,
                    token = persistedRecoveryToken.Token
                }, CancellationToken.None, fireAndForget: true);
                pubSw.Stop();
                _logger.LogDebug("Enqueued usuario.recuperacion publish in {Elapsed}ms", pubSw.ElapsedMilliseconds);
            }

            return Ok(new { message = "Si el correo existe, se enviaron instrucciones de recuperacion" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error en flujo de recuperacion para {Email}", request.Email);
            return Ok(new { message = "Si el correo existe, se enviaron instrucciones de recuperacion" });
        }
    }

    [HttpPost("reset-password")]
    public async Task<IActionResult> ResetPassword([FromBody] ResetPasswordRequest request)
    {
        var tokenValue = request.Token.Trim();
        var resetToken = await _dbContext.PasswordResetTokens
            .Include(x => x.User)
            .FirstOrDefaultAsync(x => x.Token == tokenValue);

        if (resetToken is null || resetToken.IsUsed || resetToken.ExpiresAt <= DateTimeOffset.UtcNow || resetToken.User is null)
        {
            return BadRequest(new { message = "Token de recuperacion invalido o expirado" });
        }

        if (!resetToken.User.IsActive)
        {
            return BadRequest(new { message = "Usuario inhabilitado" });
        }

        resetToken.User.PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.NewPassword, GetPasswordHashWorkFactor());
        resetToken.User.UpdatedAt = DateTimeOffset.UtcNow;
        resetToken.IsUsed = true;

        await _dbContext.SaveChangesAsync();

        return Ok(new { message = "Contrasena actualizada correctamente" });
    }

    [HttpPost("validate")]
    public IActionResult ValidateToken([FromBody] ValidateTokenRequest request)
    {
        var isValid = _jwtTokenService.TryValidateToken(request.Token, out var subject, out var role);

        return Ok(new
        {
            valid = isValid,
            subject,
            role
        });
    }

    [Authorize]
    [HttpGet("me")]
    public IActionResult Me()
    {
        var subject = User.Claims.FirstOrDefault(c => c.Type.EndsWith("nameidentifier", StringComparison.OrdinalIgnoreCase))?.Value
            ?? User.Claims.FirstOrDefault(c => c.Type.EndsWith("name", StringComparison.OrdinalIgnoreCase))?.Value
            ?? User.Claims.FirstOrDefault(c => c.Type.EndsWith("sub", StringComparison.OrdinalIgnoreCase))?.Value;
        var role = User.Claims.FirstOrDefault(c => c.Type.EndsWith("role", StringComparison.OrdinalIgnoreCase))?.Value;

        return Ok(new { subject, role });
    }

    private AuthResponse BuildAuthResponse(string email, string role, string token)
    {
        return new AuthResponse
        {
            AccessToken = token,
            TokenType = "Bearer",
            ExpiresInSeconds = _jwtTokenService.GetTokenDurationSeconds(),
            Email = email,
            Role = role
        };
    }

    private int GetPasswordHashWorkFactor()
    {
        var raw = Environment.GetEnvironmentVariable("AUTH_PASSWORD_HASH_WORK_FACTOR")
            ?? _configuration["Auth:PasswordHashWorkFactor"];

        if (int.TryParse(raw, out var workFactor))
        {
            return Math.Clamp(workFactor, 8, 14);
        }

        return 8;
    }

    private int GetResetTokenExpirationMinutes()
    {
        var raw = Environment.GetEnvironmentVariable("RESET_TOKEN_EXPIRATION_MINUTES")
            ?? _configuration["Auth:ResetTokenExpirationMinutes"];

        return int.TryParse(raw, out var minutes) && minutes > 0 ? minutes : 30;
    }

    private async Task<User> EnsureRecoverUserAsync(string email)
    {
        var user = await _dbContext.Users.FirstOrDefaultAsync(x => x.Email == email);
        if (user is null)
        {
            // Fallback resiliente: si el alta por evento fallo, permitir crear usuario
            // en auth al solicitar recuperacion para no bloquear el flujo.
            for (var attempt = 0; attempt < 3; attempt++)
            {
                user = new User
                {
                    Id = Guid.NewGuid(),
                    Email = email,
                    PasswordHash = string.Empty,
                    Role = "USER",
                    IsActive = true,
                    CreatedAt = DateTimeOffset.UtcNow,
                    UpdatedAt = DateTimeOffset.UtcNow
                };

                _dbContext.Users.Add(user);

                try
                {
                    await _dbContext.SaveChangesAsync();
                    break;
                }
                catch (DbUpdateException)
                {
                    _dbContext.Entry(user).State = EntityState.Detached;

                    var existingByEmail = await _dbContext.Users.FirstOrDefaultAsync(x => x.Email == email);
                    if (existingByEmail is not null)
                    {
                        user = existingByEmail;
                        break;
                    }

                    if (attempt == 2)
                    {
                        throw;
                    }
                }
            }
        }

        if (user is null)
        {
            throw new InvalidOperationException("No fue posible resolver el usuario para recuperacion");
        }

        // Importante: NO reactivar usuarios deshabilitados aquí. Si un empleado fue
        // dado de baja (empleado.eliminado -> IsActive=false), el caller de
        // RecoverPassword debe rechazar la solicitud para preservar el bloqueo.
        return user;
    }

    private static bool IsDuplicateConstraint(DbUpdateException ex, string constraintName)
    {
        return ex.InnerException is PostgresException pgEx
            && pgEx.SqlState == PostgresErrorCodes.UniqueViolation
            && string.Equals(pgEx.ConstraintName, constraintName, StringComparison.OrdinalIgnoreCase);
    }
}
