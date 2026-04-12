from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar .env desde la raíz del proyecto (retos-microservicios/.env)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.departamentos import router as departamentos_router
from app.core.security import validate_jwt_or_401

app = FastAPI(title="Servicio de Departamentos", version="1.0.0")


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
    return {"status": "ok"}