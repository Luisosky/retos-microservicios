<?php

namespace App\Http\Middleware;

use Closure;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
use Throwable;

class ValidateJwtToken
{
    public function handle(Request $request, Closure $next): Response
    {
        $authHeader = $request->header('Authorization', '');
        if (!str_starts_with($authHeader, 'Bearer ')) {
            return new JsonResponse(['message' => 'Missing or invalid Authorization header'], 401);
        }

        $token = trim(substr($authHeader, 7));
        if ($token === '') {
            return new JsonResponse(['message' => 'Missing bearer token'], 401);
        }

        $secret = env('JWT_SECRET');
        if (empty($secret)) {
            return new JsonResponse(['message' => 'JWT secret is not configured'], 500);
        }

        $issuer = env('JWT_ISSUER', 'auth-service');
        $audience = env('JWT_AUDIENCE', 'microservices-clients');

        try {
            $decoded = (array) JWT::decode($token, new Key($secret, 'HS256'));

            if (($decoded['iss'] ?? null) !== $issuer) {
                return new JsonResponse(['message' => 'Invalid token issuer'], 401);
            }

            if (($decoded['aud'] ?? null) !== $audience) {
                return new JsonResponse(['message' => 'Invalid token audience'], 401);
            }

            if (empty($decoded['sub'])) {
                return new JsonResponse(['message' => 'Invalid token subject'], 401);
            }

            $request->attributes->set('jwt.sub', (string) $decoded['sub']);
            $request->attributes->set('jwt.role', (string) ($decoded['role'] ?? ''));
        } catch (Throwable $ex) {
            return new JsonResponse(['message' => 'Invalid token: '.$ex->getMessage()], 401);
        }

        return $next($request);
    }
}
