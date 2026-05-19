namespace ServicioAutenticacion.Dtos;

public class AuthResponse
{
    public required string AccessToken { get; init; }
    public required string TokenType { get; init; }
    public required int ExpiresInSeconds { get; init; }
    public required string Email { get; init; }
    public required string Role { get; init; }
}
