import os
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request as UrlRequest, urlopen

import jwt
from fastapi import HTTPException, Request, status


def _is_public_path(path: str) -> bool:
    public_prefixes = (
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    )
    return any(path == prefix or path.startswith(prefix + "/") for prefix in public_prefixes)


def validate_jwt_or_401(request: Request) -> dict[str, Any]:
    if request.method.upper() == "OPTIONS":
        return {}

    if _is_public_path(request.url.path):
        return {}

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header[len("Bearer ") :].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret is not configured",
        )

    issuer = os.getenv("JWT_ISSUER", "auth-service")
    audience = os.getenv("JWT_AUDIENCE", "microservices-clients")

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience=audience,
            issuer=issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(exc)}",
        ) from exc

    return payload


def require_dep001_or_403(request: Request) -> dict[str, Any]:
    payload = validate_jwt_or_401(request)
    departamento_id = _resolver_departamento_id(payload, request)

    if departamento_id.upper() != "DEP001":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta operación.",
        )

    return payload


def _resolver_departamento_id(payload: dict[str, Any], request: Request) -> str:
    claim_keys = ("departamentoId", "departamento_id", "departmentId")
    for key in claim_keys:
        raw_value = payload.get(key)
        if isinstance(raw_value, str) and raw_value.strip():
            return raw_value.strip()

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pudo identificar el usuario autenticado.",
        )

    return _obtener_departamento_por_email(subject.strip(), request)


def _obtener_departamento_por_email(email: str, request: Request) -> str:
    base_url = os.getenv("EMPLEADOS_SERVICE_URL", "http://empleados-service:8080").rstrip("/")
    url = f"{base_url}/empleado/email/{quote(email, safe='')}"

    headers: dict[str, str] = {"Accept": "application/json"}
    auth_header = request.headers.get("Authorization", "")
    if auth_header:
        headers["Authorization"] = auth_header

    http_request = UrlRequest(url=url, headers=headers, method="GET")

    try:
        with urlopen(http_request, timeout=5) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        if exc.code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se encontró un empleado asociado al usuario autenticado.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible validar permisos contra el servicio de empleados.",
        ) from exc
    except (URLError, TimeoutError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible conectar con el servicio de empleados.",
        ) from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Respuesta inválida del servicio de empleados.",
        ) from exc

    departamento_id = payload.get("departamentoId") or payload.get("departamento_id")
    if not isinstance(departamento_id, str) or not departamento_id.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Respuesta inválida del servicio de empleados.",
        )

    return departamento_id.strip()
