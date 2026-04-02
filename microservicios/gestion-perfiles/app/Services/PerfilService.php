<?php

namespace App\Services;

use App\Models\Perfil;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Http;
use RuntimeException;

class PerfilService
{
    /**
     * Obtener todos los perfiles (paginado).
     */
    public function listar(int $perPage = 15): LengthAwarePaginator
    {
        return Perfil::orderBy('fecha_creacion', 'desc')->paginate($perPage);
    }

    /**
     * Buscar un perfil por su ID.
     */
    public function encontrar(string $id): ?Perfil
    {
        return Perfil::find($id);
    }

    /**
     * Buscar un perfil por el ID del empleado.
     */
    public function encontrarPorEmpleadoId(string $empleadoId): ?Perfil
    {
        return Perfil::where('empleado_id', $empleadoId)->first();
    }

    /**
     * Crear un nuevo perfil.
     */
    public function crear(array $datos): Perfil
    {
        return Perfil::create($datos);
    }

    /**
     * Actualizar un perfil existente.
     */
    public function actualizar(Perfil $perfil, array $datos): Perfil
    {
        $perfil->update($datos);
        return $perfil->fresh();
    }

    /**
     * Eliminar un perfil (soft delete).
     */
    public function eliminar(Perfil $perfil): void
    {
        $perfil->delete();
    }

    /**
     * Eliminar el perfil de un empleado eliminado (llamado desde RabbitMQ consumer).
     */
    public function desactivarPorEmpleadoId(string $empleadoId): bool
    {
        $perfil = $this->encontrarPorEmpleadoId($empleadoId);

        if (!$perfil) {
            return false;
        }

        $perfil->delete();

        return true;
    }

    /**
     * Consulta el servicio de empleados y confirma si el empleado existe.
     *
     * @throws RuntimeException Si el servicio de empleados no responde correctamente.
     */
    public function obtenerEmpleadoDesdeServicio(string $empleadoId): ?array
    {
        $baseUrl = rtrim((string) config('microservices.empleados_url'), '/');
        $rutasConsulta = [
            "/empleado/{$empleadoId}",
            "/empleados/{$empleadoId}",
        ];
        $statusError = null;
        $rawEmpleado = null;

        foreach ($rutasConsulta as $ruta) {
            try {
                $response = Http::timeout(5)
                    ->acceptJson()
                    ->get("{$baseUrl}{$ruta}");
            } catch (ConnectionException $e) {
                throw new RuntimeException('No fue posible conectar con el servicio de empleados.', 0, $e);
            }

            if ($response->status() === 404) {
                continue;
            }

            if ($response->status() === 405) {
                $statusError = 405;
                continue;
            }

            if (!$response->successful()) {
                $statusError = $response->status();
                continue;
            }

            $rawEmpleado = $response->json();
            break;
        }

        if ($rawEmpleado === null) {
            if ($statusError === null) {
                return null;
            }

            throw new RuntimeException('El servicio de empleados respondió con error.');
        }

        $empleado = $this->normalizarEmpleado($rawEmpleado);

        if ($empleado === null || empty($empleado['id']) || empty($empleado['nombre']) || empty($empleado['email'])) {
            throw new RuntimeException('Respuesta inválida del servicio de empleados.');
        }

        return $empleado;
    }

    private function normalizarEmpleado(mixed $payload): ?array
    {
        if (!is_array($payload)) {
            return null;
        }

        if (isset($payload['data']) && is_array($payload['data'])) {
            $payload = $payload['data'];
        }

        $idRaw = $payload['id'] ?? $payload['numeroEmpleado'] ?? $payload['empleadoId'] ?? null;
        $nombreRaw = $payload['nombre'] ?? null;
        $emailRaw = $payload['email'] ?? $payload['correo'] ?? null;

        $id = is_scalar($idRaw) ? trim((string) $idRaw) : '';
        $nombre = is_scalar($nombreRaw) ? trim((string) $nombreRaw) : '';
        $email = is_scalar($emailRaw) ? trim((string) $emailRaw) : '';

        if ($nombre === '' && isset($payload['apellido'])) {
            $nombre = trim(((string) ($payload['nombre'] ?? '')) . ' ' . ((string) $payload['apellido']));
        }

        if ($id === '') {
            return null;
        }

        if ($nombre === '') {
            return null;
        }

        if ($email === '') {
            return null;
        }

        return [
            'id' => $id,
            'nombre' => $nombre,
            'email' => $email,
        ];
    }

    /**
     * Crear o actualizar un perfil a partir de un evento RabbitMQ.
     */
    public function crearDesdeEvento(array $payload): Perfil
    {
        return Perfil::updateOrCreate(
            ['empleado_id' => $payload['id']],
            [
                'nombre'          => $payload['nombre'] ?? 'Sin nombre',
                'email'           => $payload['email'] ?? '',
                'telefono'        => '',
                'direccion'       => '',
                'ciudad'          => '',
                'biografia'       => '',
                'fecha_creacion'  => now(),
            ]
        );
    }
}
