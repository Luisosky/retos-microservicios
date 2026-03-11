<?php

use Illuminate\Support\Facades\Facade;
use Illuminate\Support\ServiceProvider;

return [
    'name'            => env('APP_NAME', 'Gestion Perfiles'),
    'env'             => env('APP_ENV', 'production'),
    'debug'           => (bool) env('APP_DEBUG', false),
    'url'             => env('APP_URL', 'http://localhost'),
    'timezone'        => 'America/Bogota',
    'locale'          => 'es',
    'fallback_locale' => 'es',
    'faker_locale'    => 'es_CO',
    'key'             => env('APP_KEY'),
    'cipher'          => 'AES-256-CBC',

    'providers' => ServiceProvider::defaultProviders()->merge([
        App\Providers\AppServiceProvider::class,
        App\Providers\RouteServiceProvider::class,
    ])->toArray(),

    'aliases' => Facade::defaultAliases()->merge([
        // 'Example' => App\Facades\Example::class,
    ])->toArray(),
];
