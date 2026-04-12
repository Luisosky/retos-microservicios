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
Route::prefix('perfiles')->middleware('jwt.auth')->group(function () {
    // Listar todos los perfiles
    Route::get('', [PerfilController::class, 'index']);
    Route::get('/', [PerfilController::class, 'index']);
    Route::get('/todos', [PerfilController::class, 'index']);
    Route::get('/all', [PerfilController::class, 'index']);
    
    // Obtener perfil por empleadoId
    Route::get('/{empleadoId}', [PerfilController::class, 'showByEmpleado']);
    
    // Actualizar perfil por empleadoId (compatibilidad con clientes que usan PATCH)
    Route::match(['put', 'patch'], '/{empleadoId}', [PerfilController::class, 'updateByEmpleado']);

    // Eliminar perfil por empleadoId
    Route::delete('/{empleadoId}', [PerfilController::class, 'destroyByEmpleado']);

    // Obtener/eliminar perfil por id interno (UUID)
    Route::get('/id/{id}', [PerfilController::class, 'show']);
    Route::delete('/id/{id}', [PerfilController::class, 'destroy']);
    
    // Crear un nuevo perfil (uso interno/admin)
    Route::post('/', [PerfilController::class, 'store']);
});

// Compatibilidad con clientes legacy que usan /api/perfil
Route::prefix('perfil')->middleware('jwt.auth')->group(function () {
    Route::get('', [PerfilController::class, 'index']);
    Route::get('/', [PerfilController::class, 'index']);
    Route::post('', [PerfilController::class, 'store']);
    Route::post('/', [PerfilController::class, 'store']);
    Route::get('/{empleadoId}', [PerfilController::class, 'showByEmpleado']);
    Route::match(['put', 'patch'], '/{empleadoId}', [PerfilController::class, 'updateByEmpleado']);
    Route::delete('/{empleadoId}', [PerfilController::class, 'destroyByEmpleado']);
    Route::get('/id/{id}', [PerfilController::class, 'show']);
    Route::delete('/id/{id}', [PerfilController::class, 'destroy']);
});
