from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar .env desde la raíz del proyecto (retos-microservicios/.env)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.departamentos import router as departamentos_router

app = FastAPI(title="Servicio de Departamentos", version="1.0.0")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"campo": " -> ".join(str(l) for l in e["loc"][1:]), "error": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": "Datos de entrada inválidos", "errores": errors})

app.include_router(departamentos_router)