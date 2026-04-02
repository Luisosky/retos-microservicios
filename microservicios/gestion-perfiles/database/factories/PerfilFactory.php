<?php

namespace Database\Factories;

use App\Models\Perfil;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

class PerfilFactory extends Factory
{
    protected $model = Perfil::class;

    public function definition(): array
    {
        return [
            'id'              => (string) Str::uuid(),
            'empleado_id'     => $this->faker->unique()->uuid(),
            'nombre'          => $this->faker->name(),
            'email'           => $this->faker->unique()->safeEmail(),
            'telefono'        => $this->faker->optional()->numerify('3#########'),
            'direccion'       => $this->faker->optional()->streetAddress(),
            'ciudad'          => $this->faker->optional()->city(),
            'biografia'       => $this->faker->optional()->text(200),
            'fecha_creacion'  => now(),
        ];
    }
}
