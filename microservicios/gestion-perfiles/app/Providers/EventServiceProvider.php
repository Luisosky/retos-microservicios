<?php

namespace App\Providers;

use App\Events\EmpleadoCreadoEvent;
use App\Events\EmpleadoEliminadoEvent;
use App\Listeners\HandleEmpleadoCreado;
use App\Listeners\HandleEmpleadoEliminado;
use Illuminate\Foundation\Support\Providers\EventServiceProvider as ServiceProvider;

class EventServiceProvider extends ServiceProvider
{
    /**
     * Mapeo de eventos a listeners.
     *
     * @var array<class-string, array<int, class-string>>
     */
    protected $listen = [
        EmpleadoCreadoEvent::class => [
            HandleEmpleadoCreado::class,
        ],
        EmpleadoEliminadoEvent::class => [
            HandleEmpleadoEliminado::class,
        ],
    ];

    /**
     * Registrar servicios de eventos.
     */
    public function boot(): void
    {
        //
    }

    /**
     * Determinar si los eventos y listeners deben ser auto-descubiertos.
     */
    public function shouldDiscoverEvents(): bool
    {
        return false;
    }
}
