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
    // Listar todos los perfiles
    Route::get('/', [PerfilController::class, 'index']);
    
    // Obtener perfil por empleadoId
    Route::get('/{empleadoId}', [PerfilController::class, 'showByEmpleado']);
    
    // Actualizar perfil por empleadoId
    Route::put('/{empleadoId}', [PerfilController::class, 'updateByEmpleado']);
    
    // Crear un nuevo perfil (uso interno/admin)
    Route::post('/', [PerfilController::class, 'store']);
});
