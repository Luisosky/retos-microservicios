using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace ServicioAutenticacion.Dtos;

public class RecoverPasswordRequest
{
    [Required]
    [EmailAddress]
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;
}
