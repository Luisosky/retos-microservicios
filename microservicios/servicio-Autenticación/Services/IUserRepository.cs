using ServicioAutenticacion.Models;

namespace ServicioAutenticacion.Services;

public interface IUserRepository
{
    bool Create(User user);
    User? FindByEmail(string email);
}
