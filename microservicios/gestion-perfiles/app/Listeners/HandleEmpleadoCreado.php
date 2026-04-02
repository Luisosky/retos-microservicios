<?php

namespace App\Listeners;

use App\Events\EmpleadoCreadoEvent;
use App\Services\PerfilService;
use Illuminate\Support\Facades\Log;

class HandleEmpleadoCreado
{
    public function __construct(private readonly PerfilService $perfilService) {}

    public function handle(EmpleadoCreadoEvent $event): void
    {
        try {
            // Verificar si el perfil ya existe
            $perfilExistente = $this->perfilService->encontrarPorEmpleadoId($event->id);
            if ($perfilExistente) {
                Log::warning("Intento de crear perfil para empleado que ya existe: {$event->id}");
                return;
            }

            // Crear nuevo perfil basado en los datos del empleado
            $datos = [
                'empleado_id' => $event->id,
                'nombre' => $event->nombre,
                'email' => $event->email,
            ];

            $perfil = $this->perfilService->crear($datos);

            Log::info("Perfil creado automáticamente para empleado: {$event->id}", [
                'perfil_id' => $perfil->id,
                'empleado_id' => $perfil->empleado_id,
            ]);
        } catch (\Exception $e) {
            Log::error("Error al crear perfil para empleado {$event->id}: {$e->getMessage()}", [
                'exception' => $e,
            ]);
        }
    }
}
