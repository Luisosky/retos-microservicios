using System.Text;
using System.Text.Json;
using RabbitMQ.Client;

namespace ServicioAutenticacion.Messaging;

public sealed class RabbitMqPublisher : IRabbitMqPublisher, IDisposable
{
    private const int DefaultConnectTimeoutSeconds = 5;

    private readonly IConfiguration _configuration;
    private readonly ILogger<RabbitMqPublisher> _logger;
    private readonly ConnectionFactory _factory;
    private readonly string _exchange;
    private readonly object _connectionSync = new();

    private IConnection? _connection;
    private bool _disposed;

    public RabbitMqPublisher(IConfiguration configuration, ILogger<RabbitMqPublisher> logger)
    {
        _configuration = configuration;
        _logger = logger;

        var connectTimeoutSeconds = ParseInt(
            Environment.GetEnvironmentVariable("RABBITMQ_CONNECT_TIMEOUT_SECONDS")
                ?? _configuration["RabbitMQ:ConnectTimeoutSeconds"],
            DefaultConnectTimeoutSeconds);

        var connectTimeout = TimeSpan.FromSeconds(Math.Clamp(connectTimeoutSeconds, 1, 15));

        _factory = new ConnectionFactory
        {
            HostName = Environment.GetEnvironmentVariable("RABBITMQ_HOST") ?? _configuration["RabbitMQ:Host"] ?? "rabbitmq-broker",
            Port = ParseInt(Environment.GetEnvironmentVariable("RABBITMQ_PORT") ?? _configuration["RabbitMQ:Port"], 5672),
            UserName = Environment.GetEnvironmentVariable("RABBITMQ_USERNAME") ?? _configuration["RabbitMQ:Username"] ?? "guest",
            Password = Environment.GetEnvironmentVariable("RABBITMQ_PASSWORD") ?? _configuration["RabbitMQ:Password"] ?? "guest",
            RequestedConnectionTimeout = connectTimeout,
            ContinuationTimeout = connectTimeout,
            HandshakeContinuationTimeout = connectTimeout,
            AutomaticRecoveryEnabled = true,
            TopologyRecoveryEnabled = true,
            NetworkRecoveryInterval = TimeSpan.FromSeconds(3)
        };

        _exchange = Environment.GetEnvironmentVariable("AUTH_EXCHANGE")
            ?? _configuration["RabbitMQ:Exchange"]
            ?? "empleados.events";
    }

    public Task PublishAsync(string routingKey, object payload, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();

        try
        {
            var connection = GetOrCreateConnection();
            using var channel = connection.CreateModel();

            channel.ExchangeDeclare(exchange: _exchange, type: ExchangeType.Topic, durable: true, autoDelete: false);

            var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(payload));
            var properties = channel.CreateBasicProperties();
            properties.Persistent = true;

            channel.BasicPublish(
                exchange: _exchange,
                routingKey: routingKey,
                basicProperties: properties,
                body: body
            );
        }
        catch (Exception ex)
        {
            InvalidateConnection();
            _logger.LogError(ex, "Error publicando evento RabbitMQ {RoutingKey}", routingKey);
            throw;
        }

        return Task.CompletedTask;
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        InvalidateConnection();
    }

    private IConnection GetOrCreateConnection()
    {
        lock (_connectionSync)
        {
            if (_connection is { IsOpen: true })
            {
                return _connection;
            }

            _connection?.Dispose();
            _connection = _factory.CreateConnection();
            return _connection;
        }
    }

    private void InvalidateConnection()
    {
        lock (_connectionSync)
        {
            _connection?.Dispose();
            _connection = null;
        }
    }

    private static int ParseInt(string? rawValue, int defaultValue)
    {
        return int.TryParse(rawValue, out var parsed) ? parsed : defaultValue;
    }
}
