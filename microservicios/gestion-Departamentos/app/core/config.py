from pydantic import BaseModel
import os
from urllib.parse import quote_plus

class Settings(BaseModel):
    db_host: str = os.getenv("DEP_DB_HOST", "localhost")
    db_port: int = int(os.getenv("DEP_DB_PORT", "5432"))
    db_name: str = os.getenv("DEP_DB_NAME", "Departamentos")
    db_user: str = os.getenv("DEP_DB_USER", "postgres")
    db_password: str = os.getenv("DEP_DB_PASSWORD", "password")

    @property
    def sqlalchemy_database_uri(self) -> str:
        # Escapar caracteres especiales en la contraseña
        escaped_password = quote_plus(self.db_password)
        return f"postgresql+psycopg2://{self.db_user}:{escaped_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()