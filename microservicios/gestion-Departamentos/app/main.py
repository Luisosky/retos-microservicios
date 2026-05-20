from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar .env desde la raíz del proyecto (retos-microservicios/.env)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.departamentos import router as departamentos_router
from app.core.database import engine
from app.core.observability import (
    install_json_logging,
    install_metrics,
    install_tracing,
)
from app.core.security import validate_jwt_or_401

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "departamentos-service")

# Logs JSON antes de cualquier otra cosa para que el resto del arranque también se registre con formato
install_json_logging(SERVICE_NAME)

app = FastAPI(title="Servicio de Departamentos", version="1.0.0")

# Observabilidad: métricas (/metrics) + trazas distribuidas → Zipkin
install_metrics(app, SERVICE_NAME)
install_tracing(app, SERVICE_NAME)


@app.middleware("http")
async def jwt_auth_middleware(request: Request, call_next):
    try:
        validate_jwt_or_401(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"campo": " -> ".join(str(l) for l in e["loc"][1:]), "error": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": "Datos de entrada inválidos", "errores": errors})

app.include_router(departamentos_router)


@app.get("/health")
def health_check():
    """
    Health-check con verificación real de la base de datos.

    Devuelve el contrato del Reto 7: {status, service, checks: {database, ...}}
    y un HTTP 503 cuando algún chequeo falla.
    """
    checks = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = "UP"
    except Exception:
        checks["database"] = "DOWN"

    overall = "UP" if all(v == "UP" for v in checks.values()) else "DOWN"
    payload = {"status": overall, "service": SERVICE_NAME, "checks": checks}
    return JSONResponse(
        status_code=200 if overall == "UP" else 503, content=payload
    )
