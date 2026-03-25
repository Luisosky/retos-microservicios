<?php

namespace App\Services;

use App\Models\Perfil;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Pagination\LengthAwarePaginator;

class PerfilService
{
    /**
     * Obtener todos los perfiles (paginado).
     */
    public function listar(int $perPage = 15): LengthAwarePaginator
    {
        return Perfil::orderBy('created_at', 'desc')->paginate($perPage);
    }

    /**
     * Buscar un perfil por su ID.
     */
    public function encontrar(int $id): ?Perfil
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
     * Desactivar el perfil de un empleado eliminado (llamado desde RabbitMQ consumer).
     */
    public function desactivarPorEmpleadoId(string $empleadoId): bool
    {
        $perfil = $this->encontrarPorEmpleadoId($empleadoId);

        if (!$perfil) {
            return false;
        }

        $perfil->update(['activo' => false]);
        $perfil->delete();

        return true;
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
                'departamento_id' => $payload['departamentoId'] ?? null,
                'activo'          => true,
            ]
        );
    }
}
