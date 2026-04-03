using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ServicioAutenticacion.Dtos;
using ServicioAutenticacion.Models;
using ServicioAutenticacion.Services;

namespace ServicioAutenticacion.Controllers;

[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly IUserRepository _userRepository;
    private readonly IJwtTokenService _jwtTokenService;

    public AuthController(IUserRepository userRepository, IJwtTokenService jwtTokenService)
    {
        _userRepository = userRepository;
        _jwtTokenService = jwtTokenService;
    }

    [HttpPost("register")]
    public ActionResult<AuthResponse> Register([FromBody] RegisterRequest request)
    {
        var email = request.Email.Trim().ToLowerInvariant();

        if (_userRepository.FindByEmail(email) is not null)
        {
            return Conflict(new { message = "El usuario ya existe" });
        }

        var user = new User
        {
            Email = email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.Password),
            Role = string.IsNullOrWhiteSpace(request.Role) ? "user" : request.Role.Trim().ToLowerInvariant()
        };

        var created = _userRepository.Create(user);
        if (!created)
        {
            return Conflict(new { message = "No fue posible registrar el usuario" });
        }

        var token = _jwtTokenService.GenerateToken(user);
        return Created(string.Empty, BuildAuthResponse(user, token));
    }

    [HttpPost("login")]
    public ActionResult<AuthResponse> Login([FromBody] LoginRequest request)
    {
        var email = request.Email.Trim().ToLowerInvariant();
        var user = _userRepository.FindByEmail(email);

        if (user is null || !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
        {
            return Unauthorized(new { message = "Credenciales invalidas" });
        }

        var token = _jwtTokenService.GenerateToken(user);
        return Ok(BuildAuthResponse(user, token));
    }

    [HttpPost("validate")]
    public IActionResult ValidateToken([FromBody] ValidateTokenRequest request)
    {
        var isValid = _jwtTokenService.TryValidateToken(request.Token, out var email, out var role);

        return Ok(new
        {
            valid = isValid,
            email,
            role
        });
    }

    [Authorize]
    [HttpGet("me")]
    public IActionResult Me()
    {
        var email = User.Claims.FirstOrDefault(c => c.Type.EndsWith("email", StringComparison.OrdinalIgnoreCase))?.Value;
        var role = User.Claims.FirstOrDefault(c => c.Type.EndsWith("role", StringComparison.OrdinalIgnoreCase))?.Value;

        return Ok(new { email, role });
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
}
