"""
Pruebas unitarias para los endpoints de la API de departamentos.
"""
import pytest
from fastapi import status


class TestPostDepartamento:
    """Pruebas para el endpoint POST /departamentos."""

    def test_crear_departamento_exitoso(self, client, departamento_data):
        """Prueba que se puede crear un departamento correctamente."""
        # Act
        response = client.post("/departamentos", json=departamento_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == departamento_data["id"]
        assert data["nombre"] == departamento_data["nombre"]
        assert data["descripcion"] == departamento_data["descripcion"]

    def test_crear_departamento_sin_id(self, client):
        """Prueba que falla al crear un departamento sin id."""
        # Arrange
        data_sin_id = {
            "nombre": "Ventas",
            "descripcion": "Departamento de ventas"
        }

        # Act
        response = client.post("/departamentos", json=data_sin_id)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_crear_departamento_sin_nombre(self, client):
        """Prueba que falla al crear un departamento sin nombre."""
        # Arrange
        data_sin_nombre = {
            "id": "DEPT-004",
            "descripcion": "Departamento de ventas"
        }

        # Act
        response = client.post("/departamentos", json=data_sin_nombre)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_crear_departamento_sin_descripcion(self, client):
        """Prueba que falla al crear un departamento sin descripción."""
        # Arrange
        data_sin_descripcion = {
            "id": "DEPT-004",
            "nombre": "Ventas"
        }

        # Act
        response = client.post("/departamentos", json=data_sin_descripcion)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_crear_departamento_nombre_vacio(self, client):
        """Prueba que falla al crear un departamento con nombre vacío."""
        # Arrange
        data_nombre_vacio = {
            "id": "DEPT-004",
            "nombre": "",
            "descripcion": "Descripción válida"
        }

        # Act
        response = client.post("/departamentos", json=data_nombre_vacio)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_crear_departamento_nombre_demasiado_largo(self, client):
        """Prueba que falla al crear un departamento con nombre muy largo."""
        # Arrange
        data_nombre_largo = {
            "id": "DEPT-004",
            "nombre": "A" * 121,  # Excede el máximo de 120 caracteres
            "descripcion": "Descripción válida"
        }

        # Act
        response = client.post("/departamentos", json=data_nombre_largo)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_crear_multiples_departamentos(self, client, departamento_data_list):
        """Prueba que se pueden crear múltiples departamentos."""
        # Act & Assert
        for dep_data in departamento_data_list:
            response = client.post("/departamentos", json=dep_data)
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["id"] == dep_data["id"]


class TestGetDepartamentoById:
    """Pruebas para el endpoint GET /departamentos/{dep_id}."""

    def test_obtener_departamento_existente(self, client, departamento_data):
        """Prueba que se puede obtener un departamento existente."""
        # Arrange
        client.post("/departamentos", json=departamento_data)

        # Act
        response = client.get(f"/departamentos/{departamento_data['id']}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == departamento_data["id"]
        assert data["nombre"] == departamento_data["nombre"]
        assert data["descripcion"] == departamento_data["descripcion"]

    def test_obtener_departamento_no_existente(self, client):
        """Prueba que retorna 404 cuando el departamento no existe."""
        # Act
        response = client.get("/departamentos/DEPT-999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "DEPT-999" in data["detail"]
        assert "no existe" in data["detail"]

    def test_obtener_departamento_tras_creacion(self, client, departamento_data):
        """Prueba que un departamento recién creado se puede obtener inmediatamente."""
        # Arrange
        create_response = client.post("/departamentos", json=departamento_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # Act
        get_response = client.get(f"/departamentos/{departamento_data['id']}")

        # Assert
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json() == create_response.json()

    def test_obtener_departamento_con_caracteres_especiales(self, client):
        """Prueba que se puede buscar un departamento con caracteres especiales en el id."""
        # Arrange
        dep_data = {
            "id": "DEPT-ABC-123",
            "nombre": "Departamento Especial",
            "descripcion": "Departamento con id especial"
        }
        client.post("/departamentos", json=dep_data)

        # Act
        response = client.get(f"/departamentos/{dep_data['id']}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == dep_data["id"]


class TestGetDepartamentos:
    """Pruebas para el endpoint GET /departamentos."""

    def test_listar_departamentos_vacio(self, client):
        """Prueba que retorna una lista vacía cuando no hay departamentos."""
        # Act
        response = client.get("/departamentos")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
        assert len(data) == 0

    def test_listar_departamentos_con_datos(self, client, departamento_data_list):
        """Prueba que retorna todos los departamentos correctamente."""
        # Arrange
        for dep_data in departamento_data_list:
            client.post("/departamentos", json=dep_data)

        # Act
        response = client.get("/departamentos")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(departamento_data_list)
        assert all("id" in dep for dep in data)
        assert all("nombre" in dep for dep in data)
        assert all("descripcion" in dep for dep in data)

    def test_listar_departamentos_orden_alfabetico(self, client):
        """Prueba que los departamentos se retornan ordenados alfabéticamente."""
        # Arrange
        departamentos = [
            {"id": "DEPT-003", "nombre": "Zebra", "descripcion": "Último"},
            {"id": "DEPT-001", "nombre": "Alpha", "descripcion": "Primero"},
            {"id": "DEPT-002", "nombre": "Beta", "descripcion": "Segundo"}
        ]

        for dep_data in departamentos:
            client.post("/departamentos", json=dep_data)

        # Act
        response = client.get("/departamentos")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert data[0]["nombre"] == "Alpha"
        assert data[1]["nombre"] == "Beta"
        assert data[2]["nombre"] == "Zebra"

    def test_listar_departamentos_un_solo_elemento(self, client, departamento_data):
        """Prueba que retorna correctamente una lista con un solo departamento."""
        # Arrange
        client.post("/departamentos", json=departamento_data)

        # Act
        response = client.get("/departamentos")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == departamento_data["id"]

    def test_listar_departamentos_persistencia(self, client, departamento_data, departamento_data_2):
        """Prueba que los departamentos persisten entre llamadas."""
        # Arrange
        client.post("/departamentos", json=departamento_data)
        client.post("/departamentos", json=departamento_data_2)

        # Act
        response1 = client.get("/departamentos")
        response2 = client.get("/departamentos")

        # Assert
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json() == response2.json()
        assert len(response1.json()) == 2


class TestIntegracionCompleta:
    """Pruebas de integración completas del flujo de la API."""

    def test_flujo_completo_crud(self, client, departamento_data):
        """Prueba el flujo completo: crear, listar, obtener."""
        # 1. Verificar que la lista está vacía
        response = client.get("/departamentos")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

        # 2. Crear un departamento
        create_response = client.post("/departamentos", json=departamento_data)
        assert create_response.status_code == status.HTTP_201_CREATED

        # 3. Verificar que aparece en la lista
        list_response = client.get("/departamentos")
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()) == 1

        # 4. Obtener el departamento específico
        get_response = client.get(f"/departamentos/{departamento_data['id']}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["id"] == departamento_data["id"]

    def test_crear_y_listar_multiples(self, client, departamento_data_list):
        """Prueba crear y listar múltiples departamentos."""
        # 1. Crear varios departamentos
        for dep_data in departamento_data_list:
            response = client.post("/departamentos", json=dep_data)
            assert response.status_code == status.HTTP_201_CREATED

        # 2. Listar todos
        list_response = client.get("/departamentos")
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()) == len(departamento_data_list)

        # 3. Verificar cada uno individualmente
        for dep_data in departamento_data_list:
            get_response = client.get(f"/departamentos/{dep_data['id']}")
            assert get_response.status_code == status.HTTP_200_OK
            assert get_response.json()["nombre"] == dep_data["nombre"]
