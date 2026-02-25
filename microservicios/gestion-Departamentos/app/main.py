from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar .env desde la raíz del proyecto (retos-microservicios/.env)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI
from app.api.departamentos import router as departamentos_router

app = FastAPI(title="Servicio de Departamentos", version="1.0.0")

app.include_router(departamentos_router)