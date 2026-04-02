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
    public function show(string $id): JsonResponse
    {
        $perfil = $this->perfilService->encontrar($id);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado.'], 404);
        }

        return response()->json($this->serializarPerfil($perfil));
    }

    /**
     * GET /api/perfiles/{empleadoId}
     * Obtener un perfil por el ID del empleado.
     */
    public function showByEmpleado(string $empleadoId): JsonResponse
    {
        if (empty(trim($empleadoId))) {
            return response()->json(['message' => 'El ID de empleado no puede estar vacío.'], 400);
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
        if (empty(trim($empleadoId))) {
            return response()->json(['message' => 'El ID de empleado no puede estar vacío.'], 400);
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
    public function destroy(string $id): JsonResponse
    {
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
    public function destroyByEmpleado(string $empleadoId): JsonResponse
    {
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
     * Health check endpoint.
     */
    public function health(): JsonResponse
    {
        return response()->json([
            'status'  => 'ok',
            'service' => 'gestion-perfiles',
        ]);
    }

    private function serializarPerfil(Perfil $perfil): array
    {
        return $this->serializarPerfilArray($perfil->toArray());
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
