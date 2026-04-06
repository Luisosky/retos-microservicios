using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
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

    public AuthController(
        AuthDbContext dbContext,
        IJwtTokenService jwtTokenService,
        IRabbitMqPublisher publisher,
        IConfiguration configuration)
    {
        _dbContext = dbContext;
        _jwtTokenService = jwtTokenService;
        _publisher = publisher;
        _configuration = configuration;
    }

    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login([FromBody] LoginRequest request)
    {
        var identifier = request.GetIdentifier();
        if (string.IsNullOrWhiteSpace(identifier))
        {
            return BadRequest(new { message = "Debe enviar usuario o email" });
        }

        var user = await _dbContext.Users.FirstOrDefaultAsync(x => x.Email == identifier);

        if (user is null || !user.IsActive || string.IsNullOrWhiteSpace(user.PasswordHash)
            || !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
        {
            return Unauthorized(new { message = "Credenciales invalidas" });
        }

        var token = _jwtTokenService.GenerateToken(user);
        return Ok(BuildAuthResponse(user, token));
    }

    [HttpPost("recover-password")]
    public async Task<IActionResult> RecoverPassword([FromBody] RecoverPasswordRequest request)
    {
        var email = request.Email.Trim().ToLowerInvariant();
        var user = await _dbContext.Users.FirstOrDefaultAsync(x => x.Email == email && x.IsActive);

        if (user is null)
        {
            return Ok(new { message = "Si el correo existe, se enviaron instrucciones de recuperacion" });
        }

        var activeTokens = await _dbContext.PasswordResetTokens
            .Where(x => x.UserId == user.Id && !x.IsUsed && x.ExpiresAt > DateTimeOffset.UtcNow)
            .ToListAsync();

        foreach (var token in activeTokens)
        {
            token.IsUsed = true;
        }

        var recoveryToken = new PasswordResetToken
        {
            UserId = user.Id,
            Token = Guid.NewGuid().ToString(),
            ExpiresAt = DateTimeOffset.UtcNow.AddMinutes(GetResetTokenExpirationMinutes()),
            IsUsed = false
        };

        _dbContext.PasswordResetTokens.Add(recoveryToken);
        await _dbContext.SaveChangesAsync();

        await _publisher.PublishAsync("usuario.recuperacion", new
        {
            email,
            token = recoveryToken.Token
        });

        return Ok(new { message = "Si el correo existe, se enviaron instrucciones de recuperacion" });
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

        resetToken.User.PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.NewPassword);
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

    private AuthResponse BuildAuthResponse(User user, string token)
    {
        return new AuthResponse
        {
            AccessToken = token,
            TokenType = "Bearer",
            ExpiresInSeconds = _jwtTokenService.GetTokenDurationSeconds(),
            Email = user.Email,
            Role = user.Role
        };
    }

    private int GetResetTokenExpirationMinutes()
    {
        var raw = Environment.GetEnvironmentVariable("RESET_TOKEN_EXPIRATION_MINUTES")
            ?? _configuration["Auth:ResetTokenExpirationMinutes"];

        return int.TryParse(raw, out var minutes) && minutes > 0 ? minutes : 30;
    }
}
