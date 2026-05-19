"""
Pruebas unitarias para el servicio de departamentos.
"""
import pytest
from app.services.departamento_service import (
    create_departamento,
    get_departamento,
    list_departamentos
)
from app.schemas.departamento import DepartamentoCreate
from app.models.departamento import Departamento


class TestCreateDepartamento:
    """Pruebas para la función create_departamento."""

    def test_create_departamento_exitoso(self, db_session, departamento_data):
        """Prueba que se puede crear un departamento correctamente."""
        # Arrange
        data = DepartamentoCreate(**departamento_data)

        # Act
        resultado = create_departamento(db_session, data)

        # Assert
        assert resultado is not None
        assert resultado.id == departamento_data["id"]
        assert resultado.nombre == departamento_data["nombre"]
        assert resultado.descripcion == departamento_data["descripcion"]
        assert isinstance(resultado, Departamento)

    def test_create_departamento_persiste_en_db(self, db_session, departamento_data):
        """Prueba que el departamento creado se persiste en la base de datos."""
        # Arrange
        data = DepartamentoCreate(**departamento_data)

        # Act
        resultado = create_departamento(db_session, data)

        # Assert
        departamento_en_db = db_session.get(Departamento, departamento_data["id"])
        assert departamento_en_db is not None
        assert departamento_en_db.id == resultado.id
        assert departamento_en_db.nombre == resultado.nombre

    def test_create_multiples_departamentos(self, db_session, departamento_data_list):
        """Prueba que se pueden crear múltiples departamentos."""
        # Act
        departamentos_creados = []
        for dep_data in departamento_data_list:
            data = DepartamentoCreate(**dep_data)
            departamento = create_departamento(db_session, data)
            departamentos_creados.append(departamento)

        # Assert
        assert len(departamentos_creados) == len(departamento_data_list)
        for i, dep in enumerate(departamentos_creados):
            assert dep.id == departamento_data_list[i]["id"]
            assert dep.nombre == departamento_data_list[i]["nombre"]


class TestGetDepartamento:
    """Pruebas para la función get_departamento."""

    def test_get_departamento_existente(self, db_session, departamento_data):
        """Prueba que se puede obtener un departamento existente."""
        # Arrange
        data = DepartamentoCreate(**departamento_data)
        create_departamento(db_session, data)

        # Act
        resultado = get_departamento(db_session, departamento_data["id"])

        # Assert
        assert resultado is not None
        assert resultado.id == departamento_data["id"]
        assert resultado.nombre == departamento_data["nombre"]
        assert resultado.descripcion == departamento_data["descripcion"]

    def test_get_departamento_no_existente(self, db_session):
        """Prueba que retorna None cuando el departamento no existe."""
        # Act
        resultado = get_departamento(db_session, "DEPT-999")

        # Assert
        assert resultado is None

    def test_get_departamento_con_id_vacio(self, db_session):
        """Prueba que retorna None con un id vacío."""
        # Act
        resultado = get_departamento(db_session, "")

        # Assert
        assert resultado is None


class TestListDepartamentos:
    """Pruebas para la función list_departamentos."""

    def test_list_departamentos_vacio(self, db_session):
        """Prueba que retorna una lista vacía cuando no hay departamentos."""
        # Act
        resultado = list_departamentos(db_session)

        # Assert
        assert resultado == []
        assert len(resultado) == 0

    def test_list_departamentos_con_datos(self, db_session, departamento_data_list):
        """Prueba que retorna todos los departamentos correctamente."""
        # Arrange
        for dep_data in departamento_data_list:
            data = DepartamentoCreate(**dep_data)
            create_departamento(db_session, data)

        # Act
        resultado = list_departamentos(db_session)

        # Assert
        assert len(resultado) == len(departamento_data_list)
        assert all(isinstance(dep, Departamento) for dep in resultado)

    def test_list_departamentos_orden_alfabetico(self, db_session):
        """Prueba que los departamentos se retornan ordenados alfabéticamente por nombre."""
        # Arrange
        departamentos = [
            {"id": "DEPT-003", "nombre": "Zebra", "descripcion": "Último"},
            {"id": "DEPT-001", "nombre": "Alpha", "descripcion": "Primero"},
            {"id": "DEPT-002", "nombre": "Beta", "descripcion": "Segundo"}
        ]

        for dep_data in departamentos:
            data = DepartamentoCreate(**dep_data)
            create_departamento(db_session, data)

        # Act
        resultado = list_departamentos(db_session)

        # Assert
        assert len(resultado) == 3
        assert resultado[0].nombre == "Alpha"
        assert resultado[1].nombre == "Beta"
        assert resultado[2].nombre == "Zebra"

    def test_list_departamentos_un_solo_elemento(self, db_session, departamento_data):
        """Prueba que retorna correctamente una lista con un solo departamento."""
        # Arrange
        data = DepartamentoCreate(**departamento_data)
        create_departamento(db_session, data)

        # Act
        resultado = list_departamentos(db_session)

        # Assert
        assert len(resultado) == 1
        assert resultado[0].id == departamento_data["id"]
