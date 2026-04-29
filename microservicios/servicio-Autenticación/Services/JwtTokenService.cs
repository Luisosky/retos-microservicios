using Microsoft.IdentityModel.Tokens;
using ServicioAutenticacion.Models;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace ServicioAutenticacion.Services;

public class JwtTokenService : IJwtTokenService
{
    private const int DefaultExpirationMinutes = 60;

    private readonly IConfiguration _configuration;
    private readonly JwtSecurityTokenHandler _tokenHandler = new();
    private readonly TokenValidationParameters _tokenValidationParameters;
    private readonly SigningCredentials _signingCredentials;
    private readonly string _issuer;
    private readonly string _audience;
    private readonly int _expirationMinutes;

    public JwtTokenService(IConfiguration configuration)
    {
        _configuration = configuration;

        var jwtSection = _configuration.GetSection("Jwt");
        _issuer = Environment.GetEnvironmentVariable("JWT_ISSUER") ?? jwtSection["Issuer"] ?? "auth-service";
        _audience = Environment.GetEnvironmentVariable("JWT_AUDIENCE") ?? jwtSection["Audience"] ?? "microservices-clients";
        var secret = Environment.GetEnvironmentVariable("JWT_SECRET") ?? jwtSection["Secret"];

        if (string.IsNullOrWhiteSpace(secret))
        {
            throw new InvalidOperationException("JWT secret is not configured.");
        }

        _expirationMinutes = GetExpirationMinutes();

        var signingKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
        _signingCredentials = new SigningCredentials(signingKey, SecurityAlgorithms.HmacSha256);

        _tokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = _issuer,
            ValidateAudience = true,
            ValidAudience = _audience,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = signingKey,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30)
        };
    }

    public string GenerateToken(User user)
    {
        return GenerateToken(user.Email, user.Role);
    }

    public string GenerateToken(string email, string role)
    {
        var expiresAt = DateTime.UtcNow.AddMinutes(_expirationMinutes);
        var now = DateTimeOffset.UtcNow;

        var token = new JwtSecurityToken(
            issuer: _issuer,
            audience: _audience,
            claims:
            [
                new Claim(JwtRegisteredClaimNames.Sub, email),
                new Claim(ClaimTypes.Name, email),
                new Claim(ClaimTypes.Role, role),
                new Claim("role", role),
                new Claim(JwtRegisteredClaimNames.Iat, now.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64)
            ],
            notBefore: DateTime.UtcNow,
            expires: expiresAt,
            signingCredentials: _signingCredentials
        );

        return _tokenHandler.WriteToken(token);
    }

    public int GetTokenDurationSeconds()
    {
        return _expirationMinutes * 60;
    }

    public bool TryValidateToken(string token, out string subject, out string role)
    {
        subject = string.Empty;
        role = string.Empty;

        if (string.IsNullOrWhiteSpace(token))
        {
            return false;
        }

        try
        {
            var principal = _tokenHandler.ValidateToken(token, _tokenValidationParameters, out _);

            subject = principal.Claims.FirstOrDefault(c => c.Type == JwtRegisteredClaimNames.Sub)?.Value
                ?? principal.Claims.FirstOrDefault(c => c.Type == ClaimTypes.Name)?.Value
                ?? string.Empty;

            role = principal.Claims.FirstOrDefault(c => c.Type == ClaimTypes.Role)?.Value
                ?? principal.Claims.FirstOrDefault(c => c.Type == "role")?.Value
                ?? string.Empty;

            return !string.IsNullOrWhiteSpace(subject);
        }
        catch
        {
            return false;
        }
    }

    private int GetExpirationMinutes()
    {
        var raw = Environment.GetEnvironmentVariable("JWT_EXPIRATION_MINUTES")
            ?? _configuration.GetValue<string>("Jwt:ExpirationMinutes");

        return int.TryParse(raw, out var minutes) && minutes > 0
            ? minutes
            : DefaultExpirationMinutes;
    }
}
