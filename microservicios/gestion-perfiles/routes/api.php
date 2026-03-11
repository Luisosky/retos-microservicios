<?php

use App\Http\Controllers\PerfilController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes - Gestion de Perfiles
|--------------------------------------------------------------------------
*/

// Health check
Route::get('/health', [PerfilController::class, 'health']);

// Rutas de perfiles
Route::prefix('perfiles')->group(function () {
    Route::get('/', [PerfilController::class, 'index']);
    Route::post('/', [PerfilController::class, 'store']);
    Route::get('/empleado/{empleadoId}', [PerfilController::class, 'showByEmpleado']);
    Route::get('/{id}', [PerfilController::class, 'show']);
    Route::put('/{id}', [PerfilController::class, 'update']);
    Route::delete('/{id}', [PerfilController::class, 'destroy']);
});
