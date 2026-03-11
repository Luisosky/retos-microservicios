from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI


def _load_root_env_file() -> None:
    for parent in Path(__file__).resolve().parents:
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            break


_load_root_env_file()

from app.api.notificaciones import router as notificaciones_router
from app.core.database import Base, engine
from app.messaging.consumer import EmpleadoEventsConsumer

app = FastAPI(title="Servicio de Notificaciones", version="1.0.0")
consumer = EmpleadoEventsConsumer()


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    consumer.start()


@app.on_event("shutdown")
def shutdown_event():
    consumer.stop()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(notificaciones_router)
