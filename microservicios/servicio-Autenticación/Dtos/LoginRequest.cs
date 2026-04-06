using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace ServicioAutenticacion.Dtos;

public class LoginRequest
{
    [JsonPropertyName("usuario")]
    public string Usuario { get; set; } = string.Empty;

    [JsonPropertyName("password")]
    [Required]
    public string Password { get; set; } = string.Empty;

    [JsonPropertyName("email")]
    public string? Email { get; set; }

    public string? GetIdentifier()
    {
        var value = string.IsNullOrWhiteSpace(Usuario) ? Email : Usuario;
        return string.IsNullOrWhiteSpace(value) ? null : value.Trim().ToLowerInvariant();
    }
}
