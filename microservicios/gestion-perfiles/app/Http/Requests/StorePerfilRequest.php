<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StorePerfilRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'empleado_id'     => ['required', 'string', 'max:255', 'unique:perfiles,empleado_id'],
            'nombre'          => ['required', 'string', 'max:255'],
            'email'           => ['required', 'email', 'max:255', 'unique:perfiles,email'],
            'telefono'        => ['nullable', 'string', 'max:20'],
            'direccion'       => ['nullable', 'string', 'max:255'],
            'ciudad'          => ['nullable', 'string', 'max:100'],
            'biografia'       => ['nullable', 'string', 'max:1000'],
            'foto_url'        => ['nullable', 'url', 'max:2048'],
            'departamento_id' => ['nullable', 'string', 'max:255'],
        ];
    }

    public function messages(): array
    {
        return [
            'empleado_id.required' => 'El ID del empleado es obligatorio.',
            'empleado_id.unique'   => 'Ya existe un perfil para ese empleado.',
            'nombre.required'      => 'El nombre es obligatorio.',
            'email.required'       => 'El email es obligatorio.',
            'email.email'          => 'El email debe ser una dirección válida.',
            'email.unique'         => 'El email ya está registrado en otro perfil.',
            'telefono.max'         => 'El teléfono no debe exceder 20 caracteres.',
            'direccion.max'        => 'La dirección no debe exceder 255 caracteres.',
            'ciudad.max'           => 'La ciudad no debe exceder 100 caracteres.',
            'biografia.max'        => 'La biografía no debe exceder 1000 caracteres.',
            'foto_url.url'         => 'La URL de la foto debe ser una URL válida.',
        ];
    }
}
