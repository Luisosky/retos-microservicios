from pydantic import BaseModel
import os

class Settings(BaseModel):
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "departamentos_db")
    db_user: str = os.getenv("DB_USER", "departamentos_user")
    db_password: str = os.getenv("DB_PASSWORD", "departamentos_password")

    @property
    def sqlalchemy_database_uri(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()