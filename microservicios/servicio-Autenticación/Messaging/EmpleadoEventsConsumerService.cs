using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Npgsql;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using ServicioAutenticacion.Data;
using ServicioAutenticacion.Models;

namespace ServicioAutenticacion.Messaging;

public class EmpleadoEventsConsumerService : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly IRabbitMqPublisher _publisher;
    private readonly IConfiguration _configuration;
    private readonly ILogger<EmpleadoEventsConsumerService> _logger;

    public EmpleadoEventsConsumerService(
        IServiceScopeFactory scopeFactory,
        IRabbitMqPublisher publisher,
        IConfiguration configuration,
        ILogger<EmpleadoEventsConsumerService> logger)
    {
        _scopeFactory = scopeFactory;
        _publisher = publisher;
        _configuration = configuration;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var factory = new ConnectionFactory
                {
                    HostName = Environment.GetEnvironmentVariable("RABBITMQ_HOST") ?? _configuration["RabbitMQ:Host"] ?? "rabbitmq-broker",
                    Port = ParseInt(Environment.GetEnvironmentVariable("RABBITMQ_PORT") ?? _configuration["RabbitMQ:Port"], 5672),
                    UserName = Environment.GetEnvironmentVariable("RABBITMQ_USERNAME") ?? _configuration["RabbitMQ:Username"] ?? "guest",
                    Password = Environment.GetEnvironmentVariable("RABBITMQ_PASSWORD") ?? _configuration["RabbitMQ:Password"] ?? "guest"
                };

                var exchange = Environment.GetEnvironmentVariable("AUTH_EXCHANGE")
                    ?? _configuration["RabbitMQ:Exchange"]
                    ?? "empleados.events";

                var queue = Environment.GetEnvironmentVariable("AUTH_QUEUE")
                    ?? _configuration["RabbitMQ:Queue"]
                    ?? "auth.queue";

                using var connection = factory.CreateConnection();
                using var channel = connection.CreateModel();

                channel.ExchangeDeclare(exchange: exchange, type: ExchangeType.Topic, durable: true, autoDelete: false);
                channel.QueueDeclare(queue: queue, durable: true, exclusive: false, autoDelete: false);
                channel.QueueBind(queue: queue, exchange: exchange, routingKey: "empleado.creado");
                channel.QueueBind(queue: queue, exchange: exchange, routingKey: "empleado.eliminado");
                channel.BasicQos(0, 1, false);

                var consumer = new EventingBasicConsumer(channel);
                consumer.Received += (_, args) =>
                {
                    try
                    {
                        HandleMessage(args, stoppingToken).GetAwaiter().GetResult();
                        channel.BasicAck(args.DeliveryTag, false);
                    }
                    catch (Exception ex)
                    {
                        var shouldRequeue = IsTransient(ex);
                        _logger.LogError(ex, "Error procesando mensaje {RoutingKey}", args.RoutingKey);
                        channel.BasicNack(args.DeliveryTag, false, shouldRequeue);
                    }
                };

                channel.BasicConsume(queue: queue, autoAck: false, consumer: consumer);

                while (!stoppingToken.IsCancellationRequested)
                {
                    await Task.Delay(1000, stoppingToken);
                }
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error en consumidor de eventos de empleados. Reintentando en 5 segundos.");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }

    private async Task HandleMessage(BasicDeliverEventArgs args, CancellationToken cancellationToken)
    {
        var routingKey = args.RoutingKey;
        var payload = Encoding.UTF8.GetString(args.Body.ToArray());

        using var document = JsonDocument.Parse(payload);
        var empleadoId = document.RootElement.TryGetProperty("id", out var idElement)
            ? idElement.GetString()?.Trim()
            : null;
        if (!document.RootElement.TryGetProperty("email", out var emailElement))
        {
            _logger.LogWarning("Evento {RoutingKey} descartado: no contiene email", routingKey);
            return;
        }

        var email = emailElement.GetString()?.Trim().ToLowerInvariant();
        if (string.IsNullOrWhiteSpace(email))
        {
            _logger.LogWarning("Evento {RoutingKey} descartado: email vacio", routingKey);
            return;
        }

        using var scope = _scopeFactory.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AuthDbContext>();

        if (routingKey == "empleado.creado")
        {
            var user = await db.Users.FirstOrDefaultAsync(x => x.Email == email, cancellationToken);
            if (user is null)
            {
                // EMPLEADO_DEFAULT_PASSWORD permite que el evento empleado.creado
                // deje al usuario con una contraseña usable directamente (modo dev/E2E).
                // Si no está definido, mantenemos el flujo seguro original (hash vacío + reset token).
                var defaultPassword = Environment.GetEnvironmentVariable("EMPLEADO_DEFAULT_PASSWORD")
                    ?? _configuration["Auth:EmpleadoDefaultPassword"];
                var initialHash = string.IsNullOrWhiteSpace(defaultPassword)
                    ? string.Empty
                    : BCrypt.Net.BCrypt.HashPassword(defaultPassword, 8);

                user = new User
                {
                    Email = email,
                    PasswordHash = initialHash,
                    Role = "USER",
                    IsActive = true,
                    CreatedAt = DateTimeOffset.UtcNow,
                    UpdatedAt = DateTimeOffset.UtcNow
                };
                db.Users.Add(user);

                try
                {
                    await db.SaveChangesAsync(cancellationToken);
                }
                catch (DbUpdateException ex) when (IsDuplicateConstraint(ex, "auth_usuarios_pkey") || IsDuplicateConstraint(ex, "auth_usuarios_email_key"))
                {
                    db.Entry(user).State = EntityState.Detached;
                    var existingByEmail = await db.Users.FirstOrDefaultAsync(x => x.Email == email, cancellationToken);
                    if (existingByEmail is null)
                    {
                        throw;
                    }

                    user = existingByEmail;
                }
            }
            else
            {
                user.IsActive = true;
                user.Role = "USER";
                user.UpdatedAt = DateTimeOffset.UtcNow;
                await db.SaveChangesAsync(cancellationToken);
            }

            await db.PasswordResetTokens
                .Where(x => x.UserId == user.Id && !x.IsUsed && x.ExpiresAt > DateTimeOffset.UtcNow)
                .ExecuteUpdateAsync(setters => setters.SetProperty(t => t.IsUsed, true), cancellationToken);

            PasswordResetToken? persistedResetToken = null;
            const int maxInsertAttempts = 3;
            for (var attempt = 0; attempt < maxInsertAttempts; attempt++)
            {
                var tokenToInsert = new PasswordResetToken
                {
                    Id = Guid.NewGuid(),
                    UserId = user.Id,
                    Token = Guid.NewGuid().ToString(),
                    ExpiresAt = DateTimeOffset.UtcNow.AddMinutes(GetResetTokenExpirationMinutes()),
                    IsUsed = false
                };

                db.PasswordResetTokens.Add(tokenToInsert);
                var sw = System.Diagnostics.Stopwatch.StartNew();
                try
                {
                    await db.SaveChangesAsync(cancellationToken);
                    sw.Stop();
                    _logger.LogDebug("Saved PasswordResetToken (attempt {Attempt}) in {Elapsed}ms", attempt + 1, sw.ElapsedMilliseconds);
                    persistedResetToken = tokenToInsert;
                    break;
                }
                catch (DbUpdateException ex) when (IsDuplicateConstraint(ex, "auth_reset_tokens_pkey"))
                {
                    sw.Stop();
                    _logger.LogWarning(ex, "Duplicate key on PasswordResetToken insert (attempt {Attempt}). Checking for persisted token.", attempt + 1);
                    db.Entry(tokenToInsert).State = EntityState.Detached;

                    // The DB may have persisted the token in a previous (retried) attempt.
                    var persisted = await db.PasswordResetTokens.AsNoTracking()
                        .FirstOrDefaultAsync(x => x.Token == tokenToInsert.Token, cancellationToken);
                    if (persisted is not null)
                    {
                        persistedResetToken = persisted;
                        break;
                    }

                    if (attempt == maxInsertAttempts - 1)
                    {
                        throw;
                    }

                    await Task.Delay(50, cancellationToken);
                    continue;
                }
                catch (DbUpdateException ex) when (ex.InnerException is Npgsql.NpgsqlException pg && pg.SqlState == "23505")
                {
                    // fallback for providers that surface Npgsql directly
                    sw.Stop();
                    _logger.LogWarning(ex, "Duplicate key on PasswordResetToken insert (attempt {Attempt}). Checking for persisted token.", attempt + 1);
                    db.Entry(tokenToInsert).State = EntityState.Detached;

                    var persisted = await db.PasswordResetTokens.AsNoTracking()
                        .FirstOrDefaultAsync(x => x.Token == tokenToInsert.Token, cancellationToken);
                    if (persisted is not null)
                    {
                        persistedResetToken = persisted;
                        break;
                    }

                    if (attempt == maxInsertAttempts - 1)
                    {
                        throw;
                    }

                    await Task.Delay(50, cancellationToken);
                    continue;
                }
            }

            if (persistedResetToken is not null)
            {
                // publish without blocking
                await _publisher.PublishAsync("usuario.creado", new
                {
                    id = string.IsNullOrWhiteSpace(empleadoId) ? null : empleadoId,
                    email,
                    token = persistedResetToken.Token
                }, CancellationToken.None, fireAndForget: true);
            }

            _logger.LogInformation("Usuario creado/actualizado por evento empleado.creado: {Email}", email);
            return;
        }

        if (routingKey == "empleado.eliminado")
        {
            var user = await db.Users.FirstOrDefaultAsync(x => x.Email == email, cancellationToken);
            if (user is null)
            {
                return;
            }

            user.IsActive = false;
            user.UpdatedAt = DateTimeOffset.UtcNow;

            var activeTokens = await db.PasswordResetTokens
                .Where(x => x.UserId == user.Id && !x.IsUsed)
                .ToListAsync(cancellationToken);

            foreach (var token in activeTokens)
            {
                token.IsUsed = true;
            }

            await db.SaveChangesAsync(cancellationToken);
            _logger.LogInformation("Usuario inhabilitado por evento empleado.eliminado: {Email}", email);
        }
    }

    private int GetResetTokenExpirationMinutes()
    {
        var raw = Environment.GetEnvironmentVariable("RESET_TOKEN_EXPIRATION_MINUTES")
            ?? _configuration["Auth:ResetTokenExpirationMinutes"];

        return int.TryParse(raw, out var minutes) && minutes > 0 ? minutes : 30;
    }

    private static int ParseInt(string? rawValue, int defaultValue)
    {
        return int.TryParse(rawValue, out var parsed) ? parsed : defaultValue;
    }

    private static bool IsTransient(Exception ex)
    {
        if (ex is TimeoutException)
        {
            return true;
        }

        if (ex.InnerException is not null)
        {
            return IsTransient(ex.InnerException);
        }

        return false;
    }

    private static bool IsDuplicateConstraint(DbUpdateException ex, string constraintName)
    {
        return ex.InnerException is PostgresException pgEx
            && pgEx.SqlState == PostgresErrorCodes.UniqueViolation
            && string.Equals(pgEx.ConstraintName, constraintName, StringComparison.OrdinalIgnoreCase);
    }
}
