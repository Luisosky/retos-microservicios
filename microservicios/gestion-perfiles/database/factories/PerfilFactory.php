<?php

namespace Database\Factories;

use App\Models\Perfil;
use Illuminate\Database\Eloquent\Factories\Factory;

class PerfilFactory extends Factory
{
    protected $model = Perfil::class;

    public function definition(): array
    {
        return [
            'empleado_id'     => $this->faker->unique()->uuid(),
            'nombre'          => $this->faker->name(),
            'email'           => $this->faker->unique()->safeEmail(),
            'foto_url'        => $this->faker->optional()->imageUrl(200, 200, 'people'),
            'bio'             => $this->faker->optional()->text(200),
            'departamento_id' => $this->faker->optional()->uuid(),
            'activo'          => true,
        ];
    }
}
