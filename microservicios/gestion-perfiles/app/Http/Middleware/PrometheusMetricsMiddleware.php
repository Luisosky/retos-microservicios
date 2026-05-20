<?php

namespace App\Http\Middleware;

use App\Http\Controllers\MetricsController;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/**
 * Middleware que instrumenta cada request HTTP para alimentar el endpoint
 * `/api/metrics`. Persiste contadores y suma de latencia en un archivo
 * compartido entre workers de PHP-FPM.
 */
class PrometheusMetricsMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        // No mido /api/metrics ni /api/health para no inflar las series con su propia actividad.
        $path = '/' . ltrim($request->path(), '/');
        if (in_array($path, ['/api/metrics', '/api/health'], true)) {
            return $next($request);
        }

        $start = microtime(true);
        try {
            $response = $next($request);
        } finally {
            $duration = microtime(true) - $start;
            $method = strtoupper($request->getMethod());
            // Normalizamos: usamos el patrón de ruta registrado para evitar cardinalidad alta
            $route = $request->route();
            $routeName = $route ? '/' . ltrim($route->uri(), '/') : $path;
            $status = isset($response) ? $response->getStatusCode() : 500;

            try {
                MetricsController::saveMetrics(function (array $payload) use ($method, $routeName, $status, $duration) {
                    $key = $method . '|' . $routeName . '|' . $status;
                    $payload['requests'][$key] = ($payload['requests'][$key] ?? 0) + 1;
                    $latencyKey = $method . '|' . $routeName;
                    $payload['latency_sum'][$latencyKey] = ($payload['latency_sum'][$latencyKey] ?? 0.0) + $duration;
                    $payload['latency_count'][$latencyKey] = ($payload['latency_count'][$latencyKey] ?? 0) + 1;
                    return $payload;
                });
            } catch (\Throwable $e) {
                // No bloquear la request si el persist falla.
            }
        }

        return $response;
    }
}
