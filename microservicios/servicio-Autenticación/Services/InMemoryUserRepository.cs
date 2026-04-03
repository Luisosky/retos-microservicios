using ServicioAutenticacion.Models;
using System.Collections.Concurrent;

namespace ServicioAutenticacion.Services;

public class InMemoryUserRepository : IUserRepository
{
    private readonly ConcurrentDictionary<string, User> _users = new(StringComparer.OrdinalIgnoreCase);

    public bool Create(User user)
    {
        return _users.TryAdd(user.Email.Trim().ToLowerInvariant(), user);
    }

    public User? FindByEmail(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
        {
            return null;
        }

        _users.TryGetValue(email.Trim().ToLowerInvariant(), out var user);
        return user;
    }
}
