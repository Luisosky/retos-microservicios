namespace ServicioAutenticacion.Models;

public class PasswordResetToken
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public Guid UserId { get; init; }
    public required string Token { get; init; }
    public DateTimeOffset ExpiresAt { get; init; }
    public bool IsUsed { get; set; }
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;

    public User? User { get; init; }
}
