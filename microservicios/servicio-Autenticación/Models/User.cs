namespace ServicioAutenticacion.Models;

public class User
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public required string Email { get; init; }
    public required string PasswordHash { get; init; }
    public string Role { get; init; } = "user";
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;
}
