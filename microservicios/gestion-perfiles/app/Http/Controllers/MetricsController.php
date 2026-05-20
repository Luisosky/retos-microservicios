<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;

/**
 * Expone métricas en formato Prometheus para que `prometheus-server`
 * pueda hacer scraping del microservicio de perfiles.
 *
 * Las métricas se mantienen en un fichero local (`/tmp/perfiles-metrics.json`)
 * compartido entre los workers de PHP-FPM. Se actualiza desde el middleware
 * `PrometheusMetricsMiddleware` que cuenta peticiones y latencia.
 */
class MetricsController extends Controller
{
    public const STORAGE_PATH = '/tmp/perfiles-metrics.json';

    public function index(Request $request): Response
    {
        $payload = self::loadMetrics();

        $serviceName = env('OTEL_SERVICE_NAME', 'perfiles-service');
        $pid = getmypid();
        $rss = self::processMemoryBytes();
        $uptime = self::processUptimeSeconds();

        $lines = [];

        $lines[] = '# HELP up Indica si el servicio está respondiendo';
        $lines[] = '# TYPE up gauge';
        $lines[] = sprintf('up{service="%s"} 1', $serviceName);

        $lines[] = '# HELP process_resident_memory_bytes Memoria residente (RSS) en bytes';
        $lines[] = '# TYPE process_resident_memory_bytes gauge';
        $lines[] = sprintf('process_resident_memory_bytes{service="%s",pid="%d"} %d', $serviceName, $pid, $rss);

        $lines[] = '# HELP process_uptime_seconds Segundos transcurridos desde el arranque del proceso';
        $lines[] = '# TYPE process_uptime_seconds gauge';
        $lines[] = sprintf('process_uptime_seconds{service="%s",pid="%d"} %d', $serviceName, $pid, $uptime);

        $lines[] = '# HELP http_requests_total Total de peticiones HTTP por método/ruta/status';
        $lines[] = '# TYPE http_requests_total counter';
        foreach (($payload['requests'] ?? []) as $key => $count) {
            [$method, $route, $status] = explode('|', $key);
            $lines[] = sprintf(
                'http_requests_total{service="%s",method="%s",path="%s",status="%s"} %d',
                $serviceName,
                $method,
                $route,
                $status,
                $count
            );
        }

        $lines[] = '# HELP http_request_duration_seconds_sum Tiempo total acumulado de respuesta por endpoint';
        $lines[] = '# TYPE http_request_duration_seconds_sum counter';
        foreach (($payload['latency_sum'] ?? []) as $key => $sum) {
            [$method, $route] = explode('|', $key);
            $lines[] = sprintf(
                'http_request_duration_seconds_sum{service="%s",method="%s",path="%s"} %.6f',
                $serviceName,
                $method,
                $route,
                $sum
            );
        }

        $lines[] = '# HELP http_request_duration_seconds_count Cantidad de peticiones medidas (denominador para promedio)';
        $lines[] = '# TYPE http_request_duration_seconds_count counter';
        foreach (($payload['latency_count'] ?? []) as $key => $count) {
            [$method, $route] = explode('|', $key);
            $lines[] = sprintf(
                'http_request_duration_seconds_count{service="%s",method="%s",path="%s"} %d',
                $serviceName,
                $method,
                $route,
                $count
            );
        }

        return response(implode("\n", $lines) . "\n", 200, [
            'Content-Type' => 'text/plain; version=0.0.4; charset=utf-8',
        ]);
    }

    public static function loadMetrics(): array
    {
        $path = self::STORAGE_PATH;
        if (!file_exists($path)) {
            return [];
        }
        $content = @file_get_contents($path);
        if (!$content) {
            return [];
        }
        $decoded = json_decode($content, true);
        return is_array($decoded) ? $decoded : [];
    }

    public static function saveMetrics(callable $mutator): void
    {
        $path = self::STORAGE_PATH;
        $fp = @fopen($path, 'c+');
        if ($fp === false) {
            return;
        }
        try {
            if (flock($fp, LOCK_EX)) {
                $content = stream_get_contents($fp);
                $payload = $content ? (json_decode($content, true) ?: []) : [];
                $payload = $mutator($payload) ?? $payload;
                ftruncate($fp, 0);
                rewind($fp);
                fwrite($fp, json_encode($payload));
                fflush($fp);
                flock($fp, LOCK_UN);
            }
        } finally {
            fclose($fp);
        }
    }

    private static function processMemoryBytes(): int
    {
        $status = @file_get_contents('/proc/self/status');
        if ($status && preg_match('/VmRSS:\s+(\d+)\s+kB/', $status, $m)) {
            return ((int) $m[1]) * 1024;
        }
        return memory_get_usage(true);
    }

    private static function processUptimeSeconds(): int
    {
        $stat = @file_get_contents('/proc/self/stat');
        if (!$stat) {
            return 0;
        }
        $parts = explode(' ', $stat);
        $starttime = (int) ($parts[21] ?? 0);
        $uptimeRaw = @file_get_contents('/proc/uptime');
        if (!$uptimeRaw) {
            return 0;
        }
        $systemUptime = (float) explode(' ', trim($uptimeRaw))[0];
        $hertz = 100; // CLK_TCK estándar en alpine
        $procUptime = $systemUptime - ($starttime / $hertz);
        return max(0, (int) $procUptime);
    }
}
