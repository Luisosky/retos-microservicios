using ServicioAutenticacion.Models;

namespace ServicioAutenticacion.Services;

public interface IJwtTokenService
{
    string GenerateToken(User user);
    int GetTokenDurationSeconds();
    bool TryValidateToken(string token, out string subject, out string role);
}
