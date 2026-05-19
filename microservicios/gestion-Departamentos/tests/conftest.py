"""
Configuración de fixtures para las pruebas.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app


# Configurar base de datos de pruebas (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sesión de base de datos para las pruebas.
    Se crea una nueva base de datos antes de cada prueba y se elimina después.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Crea un cliente de prueba de FastAPI con la base de datos de pruebas.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def departamento_data():
    """
    Datos de ejemplo para crear un departamento.
    """
    return {
        "id": "DEPT-001",
        "nombre": "Recursos Humanos",
        "descripcion": "Departamento encargado de la gestión del personal"
    }


@pytest.fixture
def departamento_data_2():
    """
    Segundo conjunto de datos de ejemplo para crear otro departamento.
    """
    return {
        "id": "DEPT-002",
        "nombre": "Tecnología",
        "descripcion": "Departamento de desarrollo y sistemas"
    }


@pytest.fixture
def departamento_data_list():
    """
    Lista de datos de ejemplo para múltiples departamentos.
    """
    return [
        {
            "id": "DEPT-001",
            "nombre": "Recursos Humanos",
            "descripcion": "Departamento encargado de la gestión del personal"
        },
        {
            "id": "DEPT-002",
            "nombre": "Tecnología",
            "descripcion": "Departamento de desarrollo y sistemas"
        },
        {
            "id": "DEPT-003",
            "nombre": "Finanzas",
            "descripcion": "Departamento de contabilidad y finanzas"
        }
    ]
