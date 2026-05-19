from pydantic import BaseModel
import os

class Settings(BaseModel):
    database_url: str = os.getenv("DEP_DATABASE_URL", "")

    @property
    def sqlalchemy_database_uri(self) -> str:
        if not self.database_url:
            raise ValueError("DEP_DATABASE_URL no está configurado en el .env")
        return self.database_url

settings = Settings()