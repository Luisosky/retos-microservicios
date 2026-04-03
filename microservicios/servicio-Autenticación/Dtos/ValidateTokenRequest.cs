using System.ComponentModel.DataAnnotations;

namespace ServicioAutenticacion.Dtos;

public class ValidateTokenRequest
{
    [Required]
    public string Token { get; set; } = string.Empty;
}
