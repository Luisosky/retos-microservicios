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
    private readonly TokenValidationParameters _tokenValidationParameters;

    public JwtTokenService(IConfiguration configuration)
    {
        _configuration = configuration;

        var jwtSection = _configuration.GetSection("Jwt");
        var issuer = Environment.GetEnvironmentVariable("JWT_ISSUER") ?? jwtSection["Issuer"] ?? "auth-service";
        var audience = Environment.GetEnvironmentVariable("JWT_AUDIENCE") ?? jwtSection["Audience"] ?? "microservices-clients";
        var secret = Environment.GetEnvironmentVariable("JWT_SECRET") ?? jwtSection["Secret"];

        if (string.IsNullOrWhiteSpace(secret))
        {
            throw new InvalidOperationException("JWT secret is not configured.");
        }

        _tokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = issuer,
            ValidateAudience = true,
            ValidAudience = audience,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret)),
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30)
        };
    }

    public string GenerateToken(User user)
    {
        var expiresAt = DateTime.UtcNow.AddMinutes(GetExpirationMinutes());
        var credentials = new SigningCredentials(
            _tokenValidationParameters.IssuerSigningKey!,
            SecurityAlgorithms.HmacSha256
        );

        var token = new JwtSecurityToken(
            issuer: _tokenValidationParameters.ValidIssuer,
            audience: _tokenValidationParameters.ValidAudience,
            claims:
            [
                new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
                new Claim(JwtRegisteredClaimNames.Email, user.Email),
                new Claim(ClaimTypes.Email, user.Email),
                new Claim(ClaimTypes.Role, user.Role)
            ],
            notBefore: DateTime.UtcNow,
            expires: expiresAt,
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public int GetTokenDurationSeconds()
    {
        return GetExpirationMinutes() * 60;
    }

    public bool TryValidateToken(string token, out string email, out string role)
    {
        email = string.Empty;
        role = string.Empty;

        if (string.IsNullOrWhiteSpace(token))
        {
            return false;
        }

        try
        {
            var handler = new JwtSecurityTokenHandler();
            var principal = handler.ValidateToken(token, _tokenValidationParameters, out _);

            email = principal.Claims.FirstOrDefault(c => c.Type == ClaimTypes.Email)?.Value
                ?? principal.Claims.FirstOrDefault(c => c.Type == JwtRegisteredClaimNames.Email)?.Value
                ?? string.Empty;

            role = principal.Claims.FirstOrDefault(c => c.Type == ClaimTypes.Role)?.Value
                ?? string.Empty;

            return !string.IsNullOrWhiteSpace(email);
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
