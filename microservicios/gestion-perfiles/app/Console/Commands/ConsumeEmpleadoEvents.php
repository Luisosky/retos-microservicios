<?php

namespace App\Console\Commands;

use App\Services\PerfilService;
use Illuminate\Console\Command;
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;
use Throwable;

class ConsumeEmpleadoEvents extends Command
{
    protected $signature   = 'perfiles:consume-eventos';
    protected $description = 'Consume eventos de empleados desde RabbitMQ y gestiona perfiles';

    public function __construct(private readonly PerfilService $perfilService)
    {
        parent::__construct();
    }

    public function handle(): int
    {
        $host     = config('rabbitmq.host');
        $port     = (int) config('rabbitmq.port');
        $user     = config('rabbitmq.user');
        $pass     = config('rabbitmq.pass');
        $exchange = config('rabbitmq.exchange');
        $queue    = config('rabbitmq.queue');

        $this->info("[PERFILES] Conectando a RabbitMQ en {$host}:{$port} ...");

        while (true) {
            try {
                $connection = new AMQPStreamConnection($host, $port, $user, $pass, '/', false, 'AMQPLAIN', null, 'en_US', 30, 30);
                $channel    = $connection->channel();

                $channel->exchange_declare($exchange, 'topic', false, true, false);
                $channel->queue_declare($queue, false, true, false, false);
                $channel->queue_bind($queue, $exchange, 'empleado.creado');
                $channel->queue_bind($queue, $exchange, 'empleado.eliminado');

                $this->info("[PERFILES] Escuchando cola '{$queue}' ...");

                $channel->basic_consume(
                    $queue,
                    '',
                    false,
                    false,
                    false,
                    false,
                    function (AMQPMessage $msg) use ($channel) {
                        $this->procesarMensaje($msg);
                        $channel->basic_ack($msg->getDeliveryTag());
                    }
                );

                while ($channel->is_consuming()) {
                    $channel->wait();
                }

                $channel->close();
                $connection->close();
            } catch (Throwable $e) {
                $this->error("[PERFILES] Error en consumer: {$e->getMessage()}. Reintentando en 5s...");
                sleep(5);
            }
        }
    }

    private function procesarMensaje(AMQPMessage $msg): void
    {
        try {
            $routingKey = $msg->getRoutingKey();
            $payload    = json_decode($msg->getBody(), true, 512, JSON_THROW_ON_ERROR);

            $this->info("[PERFILES] Evento recibido: {$routingKey} | Empleado: " . ($payload['id'] ?? 'desconocido'));

            match ($routingKey) {
                'empleado.creado'    => $this->manejarEmpleadoCreado($payload),
                'empleado.eliminado' => $this->manejarEmpleadoEliminado($payload),
                default              => $this->warn("[PERFILES] Routing key no reconocida: {$routingKey}"),
            };
        } catch (\JsonException $e) {
            $this->error("[PERFILES] Payload JSON inválido: {$e->getMessage()}");
        } catch (Throwable $e) {
            $this->error("[PERFILES] Error procesando mensaje: {$e->getMessage()}");
        }
    }

    private function manejarEmpleadoCreado(array $payload): void
    {
        $perfil = $this->perfilService->crearDesdeEvento($payload);
        $this->info("[PERFILES] Perfil creado/actualizado para empleado_id={$perfil->empleado_id}");
    }

    private function manejarEmpleadoEliminado(array $payload): void
    {
        $empleadoId = $payload['id'] ?? null;

        if (!$empleadoId) {
            $this->warn('[PERFILES] Evento eliminado sin ID de empleado, ignorando.');
            return;
        }

        $resultado = $this->perfilService->desactivarPorEmpleadoId($empleadoId);

        if ($resultado) {
            $this->info("[PERFILES] Perfil desactivado para empleado_id={$empleadoId}");
        } else {
            $this->warn("[PERFILES] No se encontró perfil para empleado_id={$empleadoId}");
        }
    }
}
