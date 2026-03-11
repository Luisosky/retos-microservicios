<?php

namespace Tests\Feature;

use App\Models\Perfil;
use Illuminate\Foundation\Testing\RefreshDatabase;
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
        $payload = [
            'empleado_id' => 'emp-001',
            'nombre'      => 'Juan Pérez',
            'email'       => 'juan.perez@empresa.com',
            'bio'         => 'Desarrollador backend',
        ];

        $response = $this->postJson('/api/perfiles', $payload);

        $response->assertStatus(201)
                 ->assertJsonFragment(['empleado_id' => 'emp-001', 'nombre' => 'Juan Pérez']);

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
        Perfil::factory()->create(['empleado_id' => 'emp-001', 'email' => 'a@empresa.com']);

        $response = $this->postJson('/api/perfiles', [
            'empleado_id' => 'emp-001',
            'nombre'      => 'Otro nombre',
            'email'       => 'b@empresa.com',
        ]);

        $response->assertStatus(422);
    }

    // -----------------------------------------------------------------------
    // GET /api/perfiles/{id}
    // -----------------------------------------------------------------------

    public function test_obtener_perfil_por_id(): void
    {
        $perfil = Perfil::factory()->create();

        $response = $this->getJson("/api/perfiles/{$perfil->id}");

        $response->assertStatus(200)
                 ->assertJsonFragment(['id' => $perfil->id]);
    }

    public function test_obtener_perfil_inexistente_retorna_404(): void
    {
        $response = $this->getJson('/api/perfiles/99999');

        $response->assertStatus(404);
    }

    // -----------------------------------------------------------------------
    // GET /api/perfiles/empleado/{empleadoId}
    // -----------------------------------------------------------------------

    public function test_obtener_perfil_por_empleado_id(): void
    {
        $perfil = Perfil::factory()->create(['empleado_id' => 'emp-xyz']);

        $response = $this->getJson('/api/perfiles/empleado/emp-xyz');

        $response->assertStatus(200)
                 ->assertJsonFragment(['empleado_id' => 'emp-xyz']);
    }

    public function test_obtener_perfil_por_empleado_id_inexistente_retorna_404(): void
    {
        $response = $this->getJson('/api/perfiles/empleado/emp-no-existe');

        $response->assertStatus(404);
    }

    // -----------------------------------------------------------------------
    // PUT /api/perfiles/{id}
    // -----------------------------------------------------------------------

    public function test_actualizar_perfil_exitoso(): void
    {
        $perfil = Perfil::factory()->create();

        $response = $this->putJson("/api/perfiles/{$perfil->id}", [
            'bio' => 'Nueva bio actualizada',
        ]);

        $response->assertStatus(200)
                 ->assertJsonFragment(['bio' => 'Nueva bio actualizada']);
    }

    public function test_actualizar_perfil_inexistente_retorna_404(): void
    {
        $response = $this->putJson('/api/perfiles/99999', ['bio' => 'test']);

        $response->assertStatus(404);
    }

    // -----------------------------------------------------------------------
    // DELETE /api/perfiles/{id}
    // -----------------------------------------------------------------------

    public function test_eliminar_perfil_exitoso(): void
    {
        $perfil = Perfil::factory()->create();

        $response = $this->deleteJson("/api/perfiles/{$perfil->id}");

        $response->assertStatus(204);
        $this->assertSoftDeleted('perfiles', ['id' => $perfil->id]);
    }

    public function test_eliminar_perfil_inexistente_retorna_404(): void
    {
        $response = $this->deleteJson('/api/perfiles/99999');

        $response->assertStatus(404);
    }
}
