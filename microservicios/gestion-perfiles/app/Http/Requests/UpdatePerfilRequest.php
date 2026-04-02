<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class UpdatePerfilRequest extends FormRequest
{
    protected function prepareForValidation(): void
    {
        if ($this->has('empleado_id') && !$this->has('empleadoId')) {
            $this->merge([
                'empleadoId' => $this->input('empleado_id'),
            ]);
        }
    }

    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'telefono'        => ['nullable', 'string', 'max:20'],
            'direccion'       => ['nullable', 'string', 'max:255'],
            'ciudad'          => ['nullable', 'string', 'max:100'],
            'biografia'       => ['nullable', 'string', 'max:1000'],
        ];
    }

    public function messages(): array
    {
        return [
            'telefono.max'         => 'El teléfono no debe exceder 20 caracteres.',
            'direccion.max'        => 'La dirección no debe exceder 255 caracteres.',
            'ciudad.max'           => 'La ciudad no debe exceder 100 caracteres.',
            'biografia.max'        => 'La biografía no debe exceder 1000 caracteres.',
        ];
    }
}
