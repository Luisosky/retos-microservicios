# Servicio de Autenticacion (C# / ASP.NET Core)

Proveedor de identidad del sistema con JWT de acceso, recuperacion de contrasena e integracion por eventos con RabbitMQ.

## Endpoints principales

- `POST /auth/login`
- `POST /auth/recover-password`
- `POST /auth/reset-password`
- `GET /health`

Compatibilidad legacy:

- `POST /api/auth/login`
- `POST /api/auth/recover-password`
- `POST /api/auth/reset-password`

## Integracion por eventos

Consume:

- `empleado.creado` -> crea o reactiva usuario, genera token de establecimiento y publica `usuario.creado`
- `empleado.eliminado` -> inhabilita usuario y expira tokens activos

Publica:

- `usuario.creado` con payload `{ email, token }`
- `usuario.recuperacion` con payload `{ email, token }`

## Variables de entorno

- `AUTH_DATABASE_URL` (si no existe, usa `DEP_DATABASE_URL` o `NOTIF_DATABASE_URL`)
- `JWT_ISSUER` (default: `auth-service`)
- `JWT_AUDIENCE` (default: `microservices-clients`)
- `JWT_SECRET` (obligatoria en entornos reales)
- `JWT_EXPIRATION_MINUTES` (default: `60`)
- `RESET_TOKEN_EXPIRATION_MINUTES` (default: `30`)
- `AUTH_PASSWORD_HASH_WORK_FACTOR` (default: `8`, rango recomendado `8`-`14`)
- `RABBITMQ_HOST` (default: `rabbitmq-broker`)
- `RABBITMQ_PORT` (default: `5672`)
- `RABBITMQ_USERNAME` (default: `guest`)
- `RABBITMQ_PASSWORD` (default: `guest`)
- `RABBITMQ_CONNECT_TIMEOUT_SECONDS` (default: `5`)
- `AUTH_EXCHANGE` (default: `empleados.events`)
- `AUTH_QUEUE` (default: `auth.queue`)

## Levantar con Docker

Desde la raiz del workspace:

```bash
docker compose up --build autenticacion
```
