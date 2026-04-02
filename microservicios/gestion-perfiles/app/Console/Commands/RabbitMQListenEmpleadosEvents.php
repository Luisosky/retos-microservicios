<?php

namespace App\Console\Commands;

use App\Events\EmpleadoCreadoEvent;
use App\Events\EmpleadoEliminadoEvent;
use Illuminate\Console\Command;
use Illuminate\Contracts\Events\Dispatcher;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Exchange\AMQPExchangeType;
use Illuminate\Support\Facades\Log;

class RabbitMQListenEmpleadosEvents extends Command
{
    protected $signature = 'rabbitmq:listen-empleados {--timeout=0 : Segundos antes de detener el listener (0 = indefinido)}';
    protected $description = 'Escucha eventos de empleados desde RabbitMQ y sincroniza perfiles';

    public function __construct(
        private readonly Dispatcher $eventDispatcher
    ) {
        parent::__construct();
    }

    public function handle(): int
    {
        try {
            $this->info('🚀 Iniciando listener de eventos de empleados desde RabbitMQ...');

            $connection = new AMQPStreamConnection(
                host: config('rabbitmq.host'),
                port: config('rabbitmq.port'),
                user: config('rabbitmq.user'),
                password: config('rabbitmq.pass'),
            );

            $channel = $connection->channel();

            // Declarar exchange
            $exchangeName = config('rabbitmq.exchange');
            $channel->exchange_declare(
                exchange: $exchangeName,
                type: AMQPExchangeType::TOPIC,
                auto_delete: false,
                durable: true
            );

            // Declarar cola
            $queueName = config('rabbitmq.queue');
            [$queueName, $messageCount, $consumerCount] = $channel->queue_declare(
                queue: $queueName,
                auto_delete: false,
                durable: true
            );

            // Binding: conectar cola al exchange con routing keys
            $channel->queue_bind(
                queue: $queueName,
                exchange: $exchangeName,
                routing_key: 'empleado.creado'
            );

            $channel->queue_bind(
                queue: $queueName,
                exchange: $exchangeName,
                routing_key: 'empleado.eliminado'
            );

            $this->info("✅ Conectado a RabbitMQ: {$exchangeName} -> {$queueName}");
            $this->info("⏳ Esperando mensajes... (Ctrl+C para detener)");

            $timeout = (int) $this->option('timeout');
            $startTime = time();

            $channel->basic_consume(
                queue: $queueName,
                consumer_tag: 'perfiles-consumer',
                no_local: false,
                no_ack: false,
                exclusive: false,
                nowait: false,
                callback: function ($msg) use (
                    &$startTime,
                    $timeout,
                    $queueName
                ) {
                    try {
                        $this->processMessage($msg);
                        $msg->ack();
                    } catch (\Exception $e) {
                        Log::error("Error procesando mensaje de {$queueName}: {$e->getMessage()}");
                        $msg->nack(requeue: true);
                    }

                    // Verificar timeout
                    if ($timeout > 0 && (time() - $startTime) > $timeout) {
                        throw new \Exception('Timeout alcanzado');
                    }
                }
            );

            // Iniciar consumo
            while (count($channel->callbacks)) {
                $channel->wait();
            }

            $channel->close();
            $connection->close();

            return self::SUCCESS;
        } catch (\Exception $e) {
            if (str_contains($e->getMessage(), 'Timeout alcanzado')) {
                $this->info('⏱️ Timeout alcanzado. Deteniendo listener...');
                return self::SUCCESS;
            }

            $this->error("❌ Error: {$e->getMessage()}");
            Log::error('Error en RabbitMQ listener: ' . $e->getMessage(), [
                'exception' => $e,
            ]);
            return self::FAILURE;
        }
    }

    private function processMessage(\PhpAmqpLib\Message\AMQPMessage $msg): void
    {
        $routingKey = $msg->delivery_info['routing_key'];
        $body = $msg->body;

        Log::debug("Mensaje recibido", [
            'routing_key' => $routingKey,
            'body' => $body,
        ]);

        $payload = json_decode($body, true);

        if (!$payload) {
            throw new \Exception("Payload JSON inválido: {$body}");
        }

        match ($routingKey) {
            'empleado.creado' => $this->handleEmpleadoCreado($payload),
            'empleado.eliminado' => $this->handleEmpleadoEliminado($payload),
            default => Log::warning("Routing key desconocido: {$routingKey}")
        };
    }

    private function handleEmpleadoCreado(array $payload): void
    {
        $this->info("📝 Procesando empleado.creado: {$payload['id']}");
        
        $event = EmpleadoCreadoEvent::fromPayload($payload);
        $this->eventDispatcher->dispatch($event);
    }

    private function handleEmpleadoEliminado(array $payload): void
    {
        $this->info("🗑️  Procesando empleado.eliminado: {$payload['id']}");
        
        $event = EmpleadoEliminadoEvent::fromPayload($payload);
        $this->eventDispatcher->dispatch($event);
    }
}
