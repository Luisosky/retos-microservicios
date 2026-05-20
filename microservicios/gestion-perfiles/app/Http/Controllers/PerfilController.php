<?php

namespace App\Http\Controllers;

use App\Http\Requests\StorePerfilRequest;
use App\Http\Requests\UpdatePerfilRequest;
use App\Models\Perfil;
use App\Services\PerfilService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use RuntimeException;

class PerfilController extends Controller
{
    public function __construct(private readonly PerfilService $perfilService) {}

    /**
     * GET /api/perfiles
     * Listar todos los perfiles (paginado).
     */
    public function index(Request $request): JsonResponse
    {
        $contexto = $this->resolverContextoAccesoConManejo($request);
        if ($contexto instanceof JsonResponse) {
            return $contexto;
        }

        if (!$contexto['esRecursosHumanos']) {
            return response()->json(['message' => 'No tienes permisos para esta operación.'], 403);
        }

        $perPage = (int) $request->query('per_page', 15);
        $perfiles = $this->perfilService->listar($perPage);
        $payload = $perfiles->toArray();

        $payload['data'] = array_map(fn (array $perfil) => $this->serializarPerfilArray($perfil), $payload['data']);

        return response()->json($payload);
    }

    /**
     * POST /api/perfiles
     * Crear un nuevo perfil.
     */
    public function store(StorePerfilRequest $request): JsonResponse
    {
        $contexto = $this->resolverContextoAccesoConManejo($request);
        if ($contexto instanceof JsonResponse) {
            return $contexto;
        }

        if (!$contexto['esRecursosHumanos']) {
            return response()->json(['message' => 'No tienes permisos para esta operación.'], 403);
        }

        $datos = $request->validated();
        $empleadoId = trim((string) ($datos['empleadoId'] ?? ''));

        try {
            $empleado = $this->perfilService->obtenerEmpleadoDesdeServicio($empleadoId);
        } catch (RuntimeException $e) {
            return response()->json(['message' => $e->getMessage()], 503);
        }

        if (!$empleado) {
            return response()->json(['message' => 'El empleado no existe en gestion-empleados.'], 404);
        }

        $perfil = $this->perfilService->crear([
            'empleado_id' => $empleado['id'],
            'nombre' => $empleado['nombre'],
            'email' => $empleado['email'],
            'telefono' => $datos['telefono'] ?? '',
            'direccion' => $datos['direccion'] ?? '',
            'ciudad' => $datos['ciudad'] ?? '',
            'biografia' => $datos['biografia'] ?? '',
            'fecha_creacion' => now(),
        ]);

        return response()->json($this->serializarPerfil($perfil), 201);
    }

    /**
     * GET /api/perfiles/{id}
     * Obtener un perfil por su ID.
     */
    public function show(Request $request, string $id): JsonResponse
    {
        $contexto = $this->resolverContextoAccesoConManejo($request);
        if ($contexto instanceof JsonResponse) {
            return $contexto;
        }

        $perfil = $this->perfilService->encontrar($id);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado.'], 404);
        }

        if (!$contexto['esRecursosHumanos']) {
            $empleadoIdPerfil = trim((string) $perfil->empleado_id);
            if ($empleadoIdPerfil !== (string) $contexto['empleadoId']) {
                return response()->json(['message' => 'Solo puedes acceder a tu propio perfil.'], 403);
            }
        }

        return response()->json($this->serializarPerfil($perfil));
    }

    /**
     * GET /api/perfiles/{empleadoId}
     * Obtener un perfil por el ID del empleado.
     */
    public function showByEmpleado(Request $request, string $empleadoId): JsonResponse
    {
        $contexto = $this->resolverContextoAccesoConManejo($request);
        if ($contexto instanceof JsonResponse) {
            return $contexto;
        }

        if (empty(trim($empleadoId))) {
            return response()->json(['message' => 'El ID de empleado no puede estar vacío.'], 400);
        }

        if (!$contexto['esRecursosHumanos'] && trim($empleadoId) !== (string) $contexto['empleadoId']) {
            return response()->json(['message' => 'Solo puedes acceder a tu propio perfil.'], 403);
        }

        $perfil = $this->perfilService->encontrarPorEmpleadoId($empleadoId);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado para ese empleado.'], 404);
        }

        return response()->json($this->serializarPerfil($perfil));
    }

    /**
     * PUT /api/perfiles/{empleadoId}
     * Actualizar un perfil existente por el ID del empleado.
     */
    public function updateByEmpleado(UpdatePerfilRequest $request, string $empleadoId): JsonResponse
    {
        $contexto = $this->resolverContextoAccesoConManejo($request);
        if ($contexto instanceof JsonResponse) {
            return $contexto;
        }

        if (empty(trim($empleadoId))) {
            return response()->json(['message' => 'El ID de empleado no puede estar vacío.'], 400);
        }

        if (!$contexto['esRecursosHumanos'] && trim($empleadoId) !== (string) $contexto['empleadoId']) {
            return response()->json(['message' => 'Solo puedes actualizar tu propio perfil.'], 403);
        }

        $perfil = $this->perfilService->encontrarPorEmpleadoId($empleadoId);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado para ese empleado.'], 404);
        }

        try {
            $empleado = $this->perfilService->obtenerEmpleadoDesdeServicio($empleadoId);
        } catch (RuntimeException $e) {
            return response()->json(['message' => $e->getMessage()], 503);
        }

        if (!$empleado) {
            return response()->json(['message' => 'El empleado no existe en gestion-empleados.'], 404);
        }

        $perfil = $this->perfilService->actualizar($perfil, $request->validated());

        return response()->json($this->serializarPerfil($perfil));
    }

    /**
     * DELETE /api/perfiles/{id}
     * Eliminar (soft delete) un perfil.
     */
    public function destroy(Request $request, string $id): JsonResponse
    {
        $contexto = $this->resolverContextoAccesoConManejo($request);
        if ($contexto instanceof JsonResponse) {
            return $contexto;
        }

        if (!$contexto['esRecursosHumanos']) {
            return response()->json(['message' => 'No tienes permisos para esta operación.'], 403);
        }

        $perfil = $this->perfilService->encontrar($id);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado.'], 404);
        }

        $this->perfilService->eliminar($perfil);

        return response()->json([
            'message' => 'Perfil eliminado correctamente.',
            'deleted' => true,
        ]);
    }

    /**
     * DELETE /api/perfiles/{empleadoId}
     * Eliminar (soft delete) un perfil por ID de empleado.
     */
    public function destroyByEmpleado(Request $request, string $empleadoId): JsonResponse
    {
        $contexto = $this->resolverContextoAccesoConManejo($request);
        if ($contexto instanceof JsonResponse) {
            return $contexto;
        }

        if (!$contexto['esRecursosHumanos']) {
            return response()->json(['message' => 'No tienes permisos para esta operación.'], 403);
        }

        if (empty(trim($empleadoId))) {
            return response()->json(['message' => 'El ID de empleado no puede estar vacío.'], 400);
        }

        $perfil = $this->perfilService->encontrarPorEmpleadoId($empleadoId);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado para ese empleado.'], 404);
        }

        $this->perfilService->eliminar($perfil);

        return response()->json([
            'message' => 'Perfil eliminado correctamente.',
            'deleted' => true,
        ]);
    }

    /**
     * GET /health
     * Health check con el contrato del Reto 7: incluye chequeo real de DB y RabbitMQ.
     * Devuelve 503 si algún componente está caído.
     */
    public function health(): JsonResponse
    {
        $checks = [];

        try {
            \DB::connection()->getPdo();
            \DB::connection()->select('SELECT 1');
            $checks['database'] = 'UP';
        } catch (\Throwable $e) {
            $checks['database'] = 'DOWN';
        }

        $host = (string) env('RABBITMQ_HOST', 'rabbitmq-broker');
        $port = (int) env('RABBITMQ_PORT', 5672);
        $errno = 0; $errstr = '';
        $sock = @fsockopen($host, $port, $errno, $errstr, 1.0);
        if ($sock) {
            $checks['messageBroker'] = 'UP';
            fclose($sock);
        } else {
            $checks['messageBroker'] = 'DOWN';
        }

        $status = in_array('DOWN', $checks, true) ? 'DOWN' : 'UP';
        $code = $status === 'UP' ? 200 : 503;

        return response()->json([
            'status'  => $status,
            'service' => env('OTEL_SERVICE_NAME', 'perfiles-service'),
            'checks'  => $checks,
        ], $code);
    }

    private function serializarPerfil(Perfil $perfil): array
    {
        return $this->serializarPerfilArray($perfil->toArray());
    }

    private function resolverContextoAccesoConManejo(Request $request): array|JsonResponse
    {
        try {
            return $this->perfilService->resolverContextoAcceso((string) $request->attributes->get('jwt.sub', ''));
        } catch (RuntimeException $e) {
            $mensaje = $e->getMessage();

            if ($this->esErrorDependencia($mensaje)) {
                return response()->json(['message' => $mensaje], 503);
            }

            return response()->json(['message' => $mensaje], 403);
        }
    }

    private function esErrorDependencia(string $mensaje): bool
    {
        return str_contains($mensaje, 'No fue posible conectar con el servicio de empleados')
            || str_contains($mensaje, 'El servicio de empleados respondió con error')
            || str_contains($mensaje, 'Respuesta inválida del servicio de empleados');
    }

    private function serializarPerfilArray(array $perfil): array
    {
        return [
            'id' => (string) ($perfil['id'] ?? ''),
            'empleadoId' => (string) ($perfil['empleado_id'] ?? ''),
            'nombre' => (string) ($perfil['nombre'] ?? ''),
            'email' => (string) ($perfil['email'] ?? ''),
            'telefono' => (string) ($perfil['telefono'] ?? ''),
            'direccion' => (string) ($perfil['direccion'] ?? ''),
            'ciudad' => (string) ($perfil['ciudad'] ?? ''),
            'biografia' => (string) ($perfil['biografia'] ?? ''),
            'fechaCreacion' => isset($perfil['fecha_creacion']) ? (string) $perfil['fecha_creacion'] : null,
        ];
    }
}
