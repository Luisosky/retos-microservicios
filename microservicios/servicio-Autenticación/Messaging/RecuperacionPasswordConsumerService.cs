using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Npgsql;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using ServicioAutenticacion.Data;
using ServicioAutenticacion.Models;

namespace ServicioAutenticacion.Messaging;

public class RecuperacionPasswordConsumerService : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly IRabbitMqPublisher _publisher;
    private readonly IConfiguration _configuration;
    private readonly ILogger<RecuperacionPasswordConsumerService> _logger;

    public RecuperacionPasswordConsumerService(
        IServiceScopeFactory scopeFactory,
        IRabbitMqPublisher publisher,
        IConfiguration configuration,
        ILogger<RecuperacionPasswordConsumerService> logger)
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

                var queue = Environment.GetEnvironmentVariable("RECOVERY_QUEUE")
                    ?? _configuration["RabbitMQ:RecoveryQueue"]
                    ?? "auth.recovery-password.queue";

                using var connection = factory.CreateConnection();
                using var channel = connection.CreateModel();

                channel.ExchangeDeclare(exchange: exchange, type: ExchangeType.Topic, durable: true, autoDelete: false);
                channel.QueueDeclare(queue: queue, durable: true, exclusive: false, autoDelete: false);
                channel.QueueBind(queue: queue, exchange: exchange, routingKey: "solicitud.recuperacion-password");
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
                        _logger.LogError(ex, "Error procesando mensaje de recuperación de contraseña {RoutingKey}", args.RoutingKey);
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
                _logger.LogError(ex, "Error en consumidor de recuperación de contraseña. Reintentando en 5 segundos.");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }

    private async Task HandleMessage(BasicDeliverEventArgs args, CancellationToken cancellationToken)
    {
        var routingKey = args.RoutingKey;
        var payload = Encoding.UTF8.GetString(args.Body.ToArray());

        _logger.LogInformation("Processing recovery password event: {Payload}", payload);

        using var document = JsonDocument.Parse(payload);
        
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

        // Get or create user
        var user = await db.Users.FirstOrDefaultAsync(x => x.Email == email, cancellationToken);
        if (user is null)
        {
            user = new User
            {
                Id = Guid.NewGuid(),
                Email = email,
                PasswordHash = string.Empty,
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
            catch
            {
                // If creation fails, try to reload existing user
                user = await db.Users.FirstOrDefaultAsync(x => x.Email == email, cancellationToken);
                if (user == null) throw;
            }
        }

        // Mark other active tokens as used
        var activeTokens = await db.PasswordResetTokens
            .Where(x => x.UserId == user.Id && !x.IsUsed && x.ExpiresAt > DateTimeOffset.UtcNow)
            .ToListAsync(cancellationToken);

        foreach (var token in activeTokens)
        {
            token.IsUsed = true;
        }

        // Create new reset token with retry on rare GUID collision
        PasswordResetToken? persistedRecoveryToken = null;
        const int maxInsertAttempts = 3;
            for (var attempt = 0; attempt < maxInsertAttempts; attempt++)
            {
                var tokenToInsert = new PasswordResetToken
                {
                    Id = Guid.NewGuid(),
                    UserId = user.Id,
                    Token = Guid.NewGuid().ToString(),
                    ExpiresAt = DateTimeOffset.UtcNow.AddMinutes(30),
                    IsUsed = false
                };

                db.PasswordResetTokens.Add(tokenToInsert);
                var sw = System.Diagnostics.Stopwatch.StartNew();
                try
                {
                    await db.SaveChangesAsync(cancellationToken);
                    sw.Stop();
                    _logger.LogDebug("Saved PasswordResetToken (attempt {Attempt}) in {Elapsed}ms", attempt + 1, sw.ElapsedMilliseconds);
                    persistedRecoveryToken = tokenToInsert;
                    break;
                }
                catch (DbUpdateException ex) when (IsDuplicateConstraint(ex, "auth_reset_tokens_pkey"))
                {
                    sw.Stop();
                    _logger.LogWarning(ex, "Duplicate key on PasswordResetToken insert (attempt {Attempt}). Checking for persisted token.", attempt + 1);
                    db.Entry(tokenToInsert).State = EntityState.Detached;

                    var persisted = await db.PasswordResetTokens.AsNoTracking()
                        .FirstOrDefaultAsync(x => x.Token == tokenToInsert.Token, cancellationToken);
                    if (persisted is not null)
                    {
                        persistedRecoveryToken = persisted;
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
                    sw.Stop();
                    _logger.LogWarning(ex, "Duplicate key on PasswordResetToken insert (attempt {Attempt}). Checking for persisted token.", attempt + 1);
                    db.Entry(tokenToInsert).State = EntityState.Detached;

                    var persisted = await db.PasswordResetTokens.AsNoTracking()
                        .FirstOrDefaultAsync(x => x.Token == tokenToInsert.Token, cancellationToken);
                    if (persisted is not null)
                    {
                        persistedRecoveryToken = persisted;
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

        // Publish usuario.recuperacion event asynchronously (fire-and-forget)
        if (persistedRecoveryToken is not null)
        {
            await _publisher.PublishAsync("usuario.recuperacion", new
            {
                id = user.Id,
                email = email,
                token = persistedRecoveryToken.Token
            }, CancellationToken.None, fireAndForget: true);
        }

        _logger.LogInformation("Password recovery token created for {Email}", email);
    }

    private static int ParseInt(string? value, int defaultValue = 0)
    {
        return !string.IsNullOrWhiteSpace(value) && int.TryParse(value, out var result)
            ? result
            : defaultValue;
    }

    private static bool IsTransient(Exception ex)
    {
        return ex switch
        {
            TimeoutException => true,
            InvalidOperationException => ex.Message.Contains("connection"),
            _ => false
        };
    }

    private static bool IsDuplicateConstraint(DbUpdateException ex, string constraintName)
    {
        return ex.InnerException is PostgresException pgEx
            && pgEx.SqlState == PostgresErrorCodes.UniqueViolation
            && string.Equals(pgEx.ConstraintName, constraintName, StringComparison.OrdinalIgnoreCase);
    }
}
