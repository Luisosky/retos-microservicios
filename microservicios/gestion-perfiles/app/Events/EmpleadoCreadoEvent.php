<?php

namespace App\Events;

class EmpleadoCreadoEvent
{
    public function __construct(
        public readonly string $id,
        public readonly string $nombre,
        public readonly string $email,
        public readonly ?string $departamentoId = null,
        public readonly ?string $fechaIngreso = null,
    ) {}

    public static function fromPayload(array $payload): self
    {
        return new self(
            id: $payload['id'] ?? '',
            nombre: $payload['nombre'] ?? '',
            email: $payload['email'] ?? '',
            departamentoId: $payload['departamentoId'] ?? null,
            fechaIngreso: $payload['fechaIngreso'] ?? null,
        );
    }
}
