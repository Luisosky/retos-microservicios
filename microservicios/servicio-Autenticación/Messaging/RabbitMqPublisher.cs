using System.Text;
using System.Text.Json;
using RabbitMQ.Client;

namespace ServicioAutenticacion.Messaging;

public class RabbitMqPublisher : IRabbitMqPublisher
{
    private readonly IConfiguration _configuration;

    public RabbitMqPublisher(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public Task PublishAsync(string routingKey, object payload, CancellationToken cancellationToken = default)
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

        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        channel.ExchangeDeclare(exchange: exchange, type: ExchangeType.Topic, durable: true, autoDelete: false);

        var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(payload));
        var properties = channel.CreateBasicProperties();
        properties.Persistent = true;

        channel.BasicPublish(
            exchange: exchange,
            routingKey: routingKey,
            basicProperties: properties,
            body: body
        );

        return Task.CompletedTask;
    }

    private static int ParseInt(string? rawValue, int defaultValue)
    {
        return int.TryParse(rawValue, out var parsed) ? parsed : defaultValue;
    }
}
