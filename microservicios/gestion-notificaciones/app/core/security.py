import os
from typing import Any

import jwt
from fastapi import HTTPException, Request, status


def _is_public_path(path: str) -> bool:
    public_prefixes = (
        "/health",
        "/metrics",
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
