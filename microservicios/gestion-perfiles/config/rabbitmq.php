<?php

return [
    'host'     => env('RABBITMQ_HOST', 'rabbitmq-broker'),
    'port'     => (int) env('RABBITMQ_PORT', 5672),
    'user'     => env('RABBITMQ_USER', 'guest'),
    'pass'     => env('RABBITMQ_PASS', 'guest'),
    'exchange' => env('RABBITMQ_EXCHANGE', 'empleados.events'),
    'queue'    => env('RABBITMQ_QUEUE', 'perfiles.queue'),
];
