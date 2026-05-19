using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace ServicioAutenticacion.Dtos;

public class ResetPasswordRequest
{
    [Required]
    [JsonPropertyName("token")]
    public string Token { get; set; } = string.Empty;

    [Required]
    [MinLength(8)]
    [JsonPropertyName("newPassword")]
    public string NewPassword { get; set; } = string.Empty;
}
