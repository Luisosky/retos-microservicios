using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
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
                user = new User
                {
                    Email = email,
                    PasswordHash = string.Empty,
                    Role = "USER",
                    IsActive = true,
                    CreatedAt = DateTimeOffset.UtcNow,
                    UpdatedAt = DateTimeOffset.UtcNow
                };
                db.Users.Add(user);
            }
            else
            {
                user.IsActive = true;
                user.Role = "USER";
                user.UpdatedAt = DateTimeOffset.UtcNow;
            }

            var activeTokens = await db.PasswordResetTokens
                .Where(x => x.UserId == user.Id && !x.IsUsed && x.ExpiresAt > DateTimeOffset.UtcNow)
                .ToListAsync(cancellationToken);

            foreach (var token in activeTokens)
            {
                token.IsUsed = true;
            }

            var resetToken = new PasswordResetToken
            {
                UserId = user.Id,
                Token = Guid.NewGuid().ToString(),
                ExpiresAt = DateTimeOffset.UtcNow.AddMinutes(GetResetTokenExpirationMinutes()),
                IsUsed = false
            };

            db.PasswordResetTokens.Add(resetToken);
            await db.SaveChangesAsync(cancellationToken);

            await _publisher.PublishAsync("usuario.creado", new
            {
                id = string.IsNullOrWhiteSpace(empleadoId) ? null : empleadoId,
                email,
                token = resetToken.Token
            }, cancellationToken);

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
}
