namespace ServicioAutenticacion.Models;

public class User
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public required string Email { get; init; }
    public string PasswordHash { get; set; } = string.Empty;
    public string Role { get; set; } = "USER";
    public bool IsActive { get; set; } = true;
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
    public ICollection<PasswordResetToken> ResetTokens { get; init; } = new List<PasswordResetToken>();
}
