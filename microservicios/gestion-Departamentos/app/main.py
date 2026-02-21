from fastapi import FastAPI
from app.api.departamentos import router as departamentos_router

app = FastAPI(title="Servicio de Departamentos", version="1.0.0")

app.include_router(departamentos_router)