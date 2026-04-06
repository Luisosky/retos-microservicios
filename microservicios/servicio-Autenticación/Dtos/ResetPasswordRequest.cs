using System.ComponentModel.DataAnnotations;

namespace ServicioAutenticacion.Dtos;

public class ResetPasswordRequest
{
    [Required]
    public string Token { get; set; } = string.Empty;

    [Required]
    [MinLength(8)]
    public string NewPassword { get; set; } = string.Empty;
}
