# Servicio de Autenticacion (C# / ASP.NET Core)

Microservicio REST de autenticacion en C# con JWT, siguiendo el estilo de los servicios Flask/Spring Boot del workspace.

## Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/validate`
- `GET /api/auth/me` (requiere `Authorization: Bearer <token>`)
- `GET /health`

## Variables de entorno

- `JWT_ISSUER` (default: `auth-service`)
- `JWT_AUDIENCE` (default: `microservices-clients`)
- `JWT_SECRET` (obligatoria en entornos reales)
- `JWT_EXPIRATION_MINUTES` (default: `60`)
- `ASPNETCORE_URLS` (default: `http://+:8084`)

## Levantar con Docker

Desde la raiz del workspace:

```bash
docker compose up --build autenticacion
```
