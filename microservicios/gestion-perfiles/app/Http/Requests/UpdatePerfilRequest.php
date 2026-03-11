<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdatePerfilRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        $perfilId = $this->route('id');

        return [
            'nombre'          => ['sometimes', 'required', 'string', 'max:255'],
            'email'           => ['sometimes', 'required', 'email', 'max:255', Rule::unique('perfiles', 'email')->ignore($perfilId)],
            'foto_url'        => ['nullable', 'url', 'max:2048'],
            'bio'             => ['nullable', 'string', 'max:1000'],
            'departamento_id' => ['nullable', 'string', 'max:255'],
            'activo'          => ['sometimes', 'boolean'],
        ];
    }

    public function messages(): array
    {
        return [
            'nombre.required' => 'El nombre es obligatorio.',
            'email.email'     => 'El email debe ser una dirección válida.',
            'email.unique'    => 'El email ya está registrado en otro perfil.',
            'foto_url.url'    => 'La URL de la foto debe ser una URL válida.',
        ];
    }
}
