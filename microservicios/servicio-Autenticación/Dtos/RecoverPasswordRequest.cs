using System.ComponentModel.DataAnnotations;

namespace ServicioAutenticacion.Dtos;

public class RecoverPasswordRequest
{
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;
}
