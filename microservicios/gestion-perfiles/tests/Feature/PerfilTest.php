<?php

namespace Tests\Feature;

use App\Models\Perfil;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class PerfilTest extends TestCase
{
    use RefreshDatabase;

    // -----------------------------------------------------------------------
    // Health check
    // -----------------------------------------------------------------------

    public function test_health_endpoint_retorna_ok(): void
    {
        $response = $this->getJson('/api/health');

        $response->assertStatus(200)
                 ->assertJson(['status' => 'ok', 'service' => 'gestion-perfiles']);
    }

    // -----------------------------------------------------------------------
    // GET /api/perfiles
    // -----------------------------------------------------------------------

    public function test_listar_perfiles_retorna_200(): void
    {
        Perfil::factory()->count(3)->create();

        $response = $this->getJson('/api/perfiles');

        $response->assertStatus(200)
                 ->assertJsonStructure(['data', 'total', 'per_page']);
    }

    // -----------------------------------------------------------------------
    // POST /api/perfiles
    // -----------------------------------------------------------------------

    public function test_crear_perfil_exitoso(): void
    {
        Http::fake([
            '*' => Http::response([
                'id' => 'emp-001',
                'nombre' => 'Juan Pérez',
                'email' => 'juan.perez@empresa.com',
            ], 200),
        ]);

        $payload = [
            'empleadoId' => 'emp-001',
            'biografia' => 'Desarrollador backend',
        ];

        $response = $this->postJson('/api/perfiles', $payload);

        $response->assertStatus(201)
                 ->assertJsonFragment(['empleadoId' => 'emp-001', 'nombre' => 'Juan Pérez']);

        $this->assertDatabaseHas('perfiles', ['empleado_id' => 'emp-001']);
    }

    public function test_crear_perfil_falla_sin_campos_requeridos(): void
    {
        $response = $this->postJson('/api/perfiles', []);

        $response->assertStatus(422)
                 ->assertJsonStructure(['message', 'errors']);
    }

    public function test_crear_perfil_falla_con_empleado_id_duplicado(): void
    {
        Http::fake([
            '*' => Http::response([
                'id' => 'emp-001',
                'nombre' => 'Empleado Base',
                'email' => 'a@empresa.com',
            ], 200),
        ]);

        Perfil::factory()->create(['empleado_id' => 'emp-001', 'email' => 'a@empresa.com']);

        $response = $this->postJson('/api/perfiles', [
            'empleadoId' => 'emp-001',
        ]);

        $response->assertStatus(422);
    }

    // -----------------------------------------------------------------------
    // GET /api/perfiles/{empleadoId}
    // -----------------------------------------------------------------------

    public function test_obtener_perfil_por_empleado_id(): void
    {
        Perfil::factory()->create(['empleado_id' => 'emp-xyz']);

        $response = $this->getJson('/api/perfiles/emp-xyz');

        $response->assertStatus(200)
                 ->assertJsonFragment(['empleadoId' => 'emp-xyz']);
    }

    public function test_obtener_perfil_por_empleado_id_inexistente_retorna_404(): void
    {
        $response = $this->getJson('/api/perfiles/emp-no-existe');

        $response->assertStatus(404);
    }

    // -----------------------------------------------------------------------
    // PUT /api/perfiles/{empleadoId}
    // -----------------------------------------------------------------------

    public function test_actualizar_perfil_exitoso(): void
    {
        Perfil::factory()->create(['empleado_id' => 'emp-200']);

        Http::fake([
            '*' => Http::response([
                'id' => 'emp-200',
                'nombre' => 'Nombre Empleado',
                'email' => 'empleado@empresa.com',
            ], 200),
        ]);

        $response = $this->putJson('/api/perfiles/emp-200', [
            'biografia' => 'Nueva bio actualizada',
        ]);

        $response->assertStatus(200)
                 ->assertJsonFragment(['biografia' => 'Nueva bio actualizada']);
    }

    public function test_actualizar_perfil_acepta_respuesta_empleados_con_data_y_numero_empleado(): void
    {
        Perfil::factory()->create(['empleado_id' => 'emp-201']);

        Http::fake([
            '*' => Http::response([
                'data' => [
                    'numeroEmpleado' => 'emp-201',
                    'nombre' => 'Nombre Desde Data',
                    'email' => 'data@empresa.com',
                ],
            ], 200),
        ]);

        $response = $this->putJson('/api/perfiles/emp-201', [
            'biografia' => 'Bio desde formato alterno',
        ]);

        $response->assertStatus(200)
                 ->assertJsonFragment(['biografia' => 'Bio desde formato alterno']);
    }

    public function test_actualizar_perfil_inexistente_retorna_404(): void
    {
        $response = $this->putJson('/api/perfiles/emp-404', ['biografia' => 'test']);

        $response->assertStatus(404);
    }

}
