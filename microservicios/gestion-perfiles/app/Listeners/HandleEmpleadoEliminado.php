<?php

namespace App\Listeners;

use App\Events\EmpleadoEliminadoEvent;
use App\Services\PerfilService;
use Illuminate\Support\Facades\Log;

class HandleEmpleadoEliminado
{
    public function __construct(private readonly PerfilService $perfilService) {}

    public function handle(EmpleadoEliminadoEvent $event): void
    {
        try {
            // Buscar el perfil asociado al empleado
            $perfil = $this->perfilService->encontrarPorEmpleadoId($event->id);
            
            if (!$perfil) {
                Log::warning("No se encontró perfil para empleado eliminado: {$event->id}");
                return;
            }

            // Opción 1: Eliminar completamente el perfil
            // $this->perfilService->eliminar($perfil);
            // Log::info("Perfil eliminado para empleado: {$event->id}");

            // Opción 2: Marcar como despedido en la biografía
            $this->perfilService->actualizar($perfil, [
                'biografia' => 'Despedido',
                'estado' => 'inactivo', // Si existe este campo
            ]);

            Log::info("Perfil marcado como despedido para empleado: {$event->id}", [
                'perfil_id' => $perfil->id,
            ]);
        } catch (\Exception $e) {
            Log::error("Error al procesar eliminación de perfil para empleado {$event->id}: {$e->getMessage()}", [
                'exception' => $e,
            ]);
        }
    }
}
