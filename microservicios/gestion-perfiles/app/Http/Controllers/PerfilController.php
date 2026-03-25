<?php

namespace App\Http\Controllers;

use App\Http\Requests\StorePerfilRequest;
use App\Http\Requests\UpdatePerfilRequest;
use App\Services\PerfilService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

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

        return response()->json($perfiles);
    }

    /**
     * POST /api/perfiles
     * Crear un nuevo perfil.
     */
    public function store(StorePerfilRequest $request): JsonResponse
    {
        $perfil = $this->perfilService->crear($request->validated());

        return response()->json($perfil, 201);
    }

    /**
     * GET /api/perfiles/{id}
     * Obtener un perfil por su ID.
     */
    public function show(int $id): JsonResponse
    {
        $perfil = $this->perfilService->encontrar($id);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado.'], 404);
        }

        return response()->json($perfil);
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

        return response()->json($perfil);
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

        $perfil = $this->perfilService->actualizar($perfil, $request->validated());

        return response()->json($perfil);
    }

    /**
     * DELETE /api/perfiles/{id}
     * Eliminar (soft delete) un perfil.
     */
    public function destroy(int $id): JsonResponse
    {
        $perfil = $this->perfilService->encontrar($id);

        if (!$perfil) {
            return response()->json(['message' => 'Perfil no encontrado.'], 404);
        }

        $this->perfilService->eliminar($perfil);

        return response()->json(null, 204);
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
}
