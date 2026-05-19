namespace ServicioAutenticacion.Messaging;

public interface IRabbitMqPublisher
{
    Task PublishAsync(string routingKey, object payload, CancellationToken cancellationToken = default, bool fireAndForget = false);
}
