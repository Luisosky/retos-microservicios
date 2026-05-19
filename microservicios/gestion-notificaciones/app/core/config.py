import os
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = os.getenv("NOTIF_DATABASE_URL", os.getenv("DEP_DATABASE_URL", ""))
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "rabbitmq-broker")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USERNAME", "guest")
    rabbitmq_pass: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    exchange_name: str = os.getenv("NOTIF_EXCHANGE", "empleados.events")
    queue_name: str = os.getenv("NOTIF_QUEUE", "notificaciones.queue")

    @property
    def sqlalchemy_database_uri(self) -> str:
        if not self.database_url:
            raise ValueError("NOTIF_DATABASE_URL no esta configurada")
        return self.database_url


settings = Settings()
