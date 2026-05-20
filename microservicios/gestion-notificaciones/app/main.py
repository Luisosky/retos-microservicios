import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text


def _load_root_env_file() -> None:
    for parent in Path(__file__).resolve().parents:
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            break


_load_root_env_file()

from app.api.notificaciones import router as notificaciones_router
from app.core.database import Base, engine
from app.core.observability import (
    install_json_logging,
    install_metrics,
    install_tracing,
)
from app.core.security import validate_jwt_or_401
from app.messaging.consumer import EmpleadoEventsConsumer

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "notificaciones-service")

install_json_logging(SERVICE_NAME)

app = FastAPI(title="Servicio de Notificaciones", version="1.0.0")
consumer = EmpleadoEventsConsumer()

install_metrics(app, SERVICE_NAME)
install_tracing(app, SERVICE_NAME)


@app.middleware("http")
async def jwt_auth_middleware(request: Request, call_next):
    try:
        validate_jwt_or_401(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    consumer.start()


@app.on_event("shutdown")
def shutdown_event():
    consumer.stop()


@app.get("/health")
def health_check():
    checks = {}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = "UP"
    except Exception:
        checks["database"] = "DOWN"

    # El consumer mantiene su propia conexión a RabbitMQ; usamos su flag interna.
    checks["messageBroker"] = "UP" if consumer.is_running() else "DOWN"

    overall = "UP" if all(v == "UP" for v in checks.values()) else "DOWN"
    payload = {"status": overall, "service": SERVICE_NAME, "checks": checks}
    return JSONResponse(
        status_code=200 if overall == "UP" else 503, content=payload
    )


app.include_router(notificaciones_router)
