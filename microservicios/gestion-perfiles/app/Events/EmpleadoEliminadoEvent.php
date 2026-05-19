<?php

namespace App\Events;

class EmpleadoEliminadoEvent
{
    public function __construct(
        public readonly string $id,
        public readonly string $nombre,
        public readonly string $email,
    ) {}

    public static function fromPayload(array $payload): self
    {
        return new self(
            id: $payload['id'] ?? '',
            nombre: $payload['nombre'] ?? '',
            email: $payload['email'] ?? '',
        );
    }
}
