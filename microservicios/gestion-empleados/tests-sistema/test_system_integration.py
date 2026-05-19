"""
Tests de Integración del Sistema Completo
Verifica el funcionamiento end-to-end de los microservicios
"""

import pytest
import requests
import time
import subprocess
import os
from typing import Optional

# URLs de los servicios
DEPARTAMENTOS_URL = "http://localhost:8081"
EMPLEADOS_URL = "http://localhost:8080"

# Datos de prueba
TEST_DEPARTAMENTO = {
    "id": "IT",
    "nombre": "Tecnología",
    "descripcion": "Departamento de TI"
}

TEST_EMPLEADO = {
    "id": "E001",
    "nombre": "Juan Pérez",
    "email": "juan@empresa.com",
    "departamentoId": "IT"
}

TEST_EMPLEADO_INVALIDO = {
    "id": "E002",
    "nombre": "María García",
    "email": "maria@empresa.com",
    "departamentoId": "NOEXISTE"
}


class TestSystemIntegration:
    """Tests de integración del sistema completo"""

    @classmethod
    def setup_class(cls):
        """Configuración inicial antes de ejecutar los tests"""
        print("\n" + "=" * 80)
        print("INICIANDO TESTS DEL SISTEMA")
        print("=" * 80)
        cls.wait_for_services()

    @staticmethod
    def wait_for_services(max_retries=30, delay=2):
        """Espera a que los servicios estén disponibles"""
        print("\n📡 Esperando a que los servicios estén disponibles...")

        services = {
            "Departamentos": f"{DEPARTAMENTOS_URL}/docs",
            "Empleados": f"{EMPLEADOS_URL}/v3/api-docs"
        }

        for service_name, url in services.items():
            retries = 0
            while retries < max_retries:
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        print(f"✅ {service_name} está disponible")
                        break
                except requests.exceptions.RequestException:
                    retries += 1
                    if retries == max_retries:
                        pytest.fail(f"❌ {service_name} no está disponible después de {max_retries * delay} segundos")
                    time.sleep(delay)

    @staticmethod
    def cleanup_test_data():
        """Limpia los datos de prueba existentes"""
        print("\n🧹 Limpiando datos de prueba previos...")

        # Intentar eliminar empleado de prueba
        try:
            requests.delete(f"{EMPLEADOS_URL}/empleados/{TEST_EMPLEADO['id']}")
        except:
            pass

        # Intentar eliminar departamento de prueba
        try:
            requests.delete(f"{DEPARTAMENTOS_URL}/departamentos/{TEST_DEPARTAMENTO['id']}")
        except:
            pass

    def test_01_crear_departamento(self):
        """
        Test 1: Crear un departamento
        Verifica que se pueda crear un departamento correctamente
        """
        print("\n" + "-" * 80)
        print("TEST 1: Crear un departamento")
        print("-" * 80)

        # Limpiar datos previos
        self.cleanup_test_data()

        # Crear departamento
        print(f"📤 Enviando petición POST a {DEPARTAMENTOS_URL}/departamentos")
        print(f"📦 Datos: {TEST_DEPARTAMENTO}")

        response = requests.post(
            f"{DEPARTAMENTOS_URL}/departamentos",
            json=TEST_DEPARTAMENTO
        )

        print(f"📥 Respuesta: Status {response.status_code}")
        print(f"📄 Body: {response.json()}")

        assert response.status_code in [200, 201], \
            f"Error al crear departamento. Status: {response.status_code}, Body: {response.text}"

        data = response.json()
        assert data["id"] == TEST_DEPARTAMENTO["id"]
        assert data["nombre"] == TEST_DEPARTAMENTO["nombre"]

        print("✅ Departamento creado exitosamente")

    def test_02_crear_empleado_asociado(self):
        """
        Test 2: Crear un empleado asociado al departamento
        Verifica que se pueda crear un empleado vinculado a un departamento existente
        """
        print("\n" + "-" * 80)
        print("TEST 2: Crear un empleado asociado al departamento")
        print("-" * 80)

        print(f"📤 Enviando petición POST a {EMPLEADOS_URL}/empleados")
        print(f"📦 Datos: {TEST_EMPLEADO}")

        response = requests.post(
            f"{EMPLEADOS_URL}/empleados",
            json=TEST_EMPLEADO
        )

        print(f"📥 Respuesta: Status {response.status_code}")
        print(f"📄 Body: {response.json()}")

        assert response.status_code in [200, 201], \
            f"Error al crear empleado. Status: {response.status_code}, Body: {response.text}"

        data = response.json()
        assert data["id"] == TEST_EMPLEADO["id"]
        assert data["nombre"] == TEST_EMPLEADO["nombre"]
        assert data["email"] == TEST_EMPLEADO["email"]
        assert data["departamentoId"] == TEST_EMPLEADO["departamentoId"]

        print("✅ Empleado creado exitosamente")

    def test_03_verificar_empleado_existe(self):
        """
        Test 3: Verificar que el empleado existe
        Consulta el empleado creado para verificar que se guardó correctamente
        """
        print("\n" + "-" * 80)
        print("TEST 3: Verificar que el empleado existe")
        print("-" * 80)

        empleado_id = TEST_EMPLEADO["id"]
        print(f"📤 Enviando petición GET a {EMPLEADOS_URL}/empleados/{empleado_id}")

        response = requests.get(f"{EMPLEADOS_URL}/empleados/{empleado_id}")

        print(f"📥 Respuesta: Status {response.status_code}")
        print(f"📄 Body: {response.json()}")

        assert response.status_code == 200, \
            f"Empleado no encontrado. Status: {response.status_code}"

        data = response.json()
        assert data["id"] == TEST_EMPLEADO["id"]
        assert data["nombre"] == TEST_EMPLEADO["nombre"]

        print("✅ Empleado encontrado exitosamente")

    def test_04_crear_empleado_departamento_inexistente(self):
        """
        Test 4: Intentar crear un empleado con departamento inexistente
        Verifica que el sistema rechace la creación de empleados con departamentos inválidos
        """
        print("\n" + "-" * 80)
        print("TEST 4: Intentar crear empleado con departamento inexistente (debe fallar)")
        print("-" * 80)

        print(f"📤 Enviando petición POST a {EMPLEADOS_URL}/empleados")
        print(f"📦 Datos: {TEST_EMPLEADO_INVALIDO}")

        response = requests.post(
            f"{EMPLEADOS_URL}/empleados",
            json=TEST_EMPLEADO_INVALIDO
        )

        print(f"📥 Respuesta: Status {response.status_code}")
        print(f"📄 Body: {response.text}")

        assert response.status_code == 400, \
            f"Se esperaba error 400 pero se recibió {response.status_code}"

        print("✅ Sistema rechazó correctamente el empleado con departamento inexistente")

    def test_05_listar_empleados(self):
        """
        Test 5: Listar empleados
        Verifica que se puedan obtener todos los empleados
        """
        print("\n" + "-" * 80)
        print("TEST 5: Listar todos los empleados")
        print("-" * 80)

        print(f"📤 Enviando petición GET a {EMPLEADOS_URL}/empleados")

        response = requests.get(f"{EMPLEADOS_URL}/empleados")

        print(f"📥 Respuesta: Status {response.status_code}")
        data = response.json()
        print(f"📄 Se encontraron {len(data)} empleados")

        assert response.status_code == 200
        assert len(data) > 0, "No se encontraron empleados"

        # Verificar que nuestro empleado está en la lista
        empleado_encontrado = any(e["id"] == TEST_EMPLEADO["id"] for e in data)
        assert empleado_encontrado, "El empleado creado no aparece en la lista"

        print("✅ Lista de empleados obtenida exitosamente")

    def test_06_listar_departamentos(self):
        """
        Test 6: Listar departamentos
        Verifica que se puedan obtener todos los departamentos
        """
        print("\n" + "-" * 80)
        print("TEST 6: Listar todos los departamentos")
        print("-" * 80)

        print(f"📤 Enviando petición GET a {DEPARTAMENTOS_URL}/departamentos")

        response = requests.get(f"{DEPARTAMENTOS_URL}/departamentos")

        print(f"📥 Respuesta: Status {response.status_code}")
        data = response.json()
        print(f"📄 Se encontraron {len(data)} departamentos")

        assert response.status_code == 200
        assert len(data) > 0, "No se encontraron departamentos"

        # Verificar que nuestro departamento está en la lista
        dept_encontrado = any(d["id"] == TEST_DEPARTAMENTO["id"] for d in data)
        assert dept_encontrado, "El departamento creado no aparece en la lista"

        print("✅ Lista de departamentos obtenida exitosamente")

    def test_07_actualizar_empleado(self):
        """
        Test 7: Actualizar un empleado
        Verifica que se pueda actualizar la información de un empleado
        """
        print("\n" + "-" * 80)
        print("TEST 7: Actualizar un empleado")
        print("-" * 80)

        empleado_id = TEST_EMPLEADO["id"]
        empleado_actualizado = TEST_EMPLEADO.copy()
        empleado_actualizado["nombre"] = "Juan Pérez Actualizado"
        empleado_actualizado["email"] = "juan.actualizado@empresa.com"

        print(f"📤 Enviando petición PUT a {EMPLEADOS_URL}/empleados/{empleado_id}")
        print(f"📦 Datos: {empleado_actualizado}")

        response = requests.put(
            f"{EMPLEADOS_URL}/empleados/{empleado_id}",
            json=empleado_actualizado
        )

        print(f"📥 Respuesta: Status {response.status_code}")
        print(f"📄 Body: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == empleado_actualizado["nombre"]
        assert data["email"] == empleado_actualizado["email"]

        print("✅ Empleado actualizado exitosamente")

    def test_08_verificar_cache_redis(self):
        """
        Test 8: Verificar que Redis está funcionando
        Realiza varias consultas para verificar que el caché funciona
        """
        print("\n" + "-" * 80)
        print("TEST 8: Verificar funcionamiento de caché Redis")
        print("-" * 80)

        empleado_id = TEST_EMPLEADO["id"]

        # Primera consulta (debe ir a la base de datos)
        print("📤 Primera consulta (sin caché)")
        start_time = time.time()
        response1 = requests.get(f"{EMPLEADOS_URL}/empleados/{empleado_id}")
        time1 = time.time() - start_time

        assert response1.status_code == 200
        print(f"⏱️ Tiempo de respuesta: {time1:.4f}s")

        # Segunda consulta (debería venir del caché y ser más rápida)
        print("📤 Segunda consulta (con caché)")
        start_time = time.time()
        response2 = requests.get(f"{EMPLEADOS_URL}/empleados/{empleado_id}")
        time2 = time.time() - start_time

        assert response2.status_code == 200
        print(f"⏱️ Tiempo de respuesta: {time2:.4f}s")

        # Verificar que el contenido es el mismo
        assert response1.json() == response2.json()

        print("✅ Caché Redis funcionando correctamente")

    def test_09_eliminar_empleado(self):
        """
        Test 9: Eliminar un empleado
        Verifica que se pueda eliminar un empleado
        """
        print("\n" + "-" * 80)
        print("TEST 9: Eliminar un empleado")
        print("-" * 80)

        empleado_id = TEST_EMPLEADO["id"]
        print(f"📤 Enviando petición DELETE a {EMPLEADOS_URL}/empleados/{empleado_id}")

        response = requests.delete(f"{EMPLEADOS_URL}/empleados/{empleado_id}")

        print(f"📥 Respuesta: Status {response.status_code}")

        assert response.status_code in [200, 204]

        # Verificar que el empleado ya no existe
        print("🔍 Verificando que el empleado fue eliminado")
        response_get = requests.get(f"{EMPLEADOS_URL}/empleados/{empleado_id}")
        assert response_get.status_code == 404

        print("✅ Empleado eliminado exitosamente")

    def test_10_eliminar_departamento(self):
        """
        Test 10: Eliminar un departamento
        Verifica que se pueda eliminar un departamento
        """
        print("\n" + "-" * 80)
        print("TEST 10: Eliminar un departamento")
        print("-" * 80)

        dept_id = TEST_DEPARTAMENTO["id"]
        print(f"📤 Enviando petición DELETE a {DEPARTAMENTOS_URL}/departamentos/{dept_id}")

        response = requests.delete(f"{DEPARTAMENTOS_URL}/departamentos/{dept_id}")

        print(f"📥 Respuesta: Status {response.status_code}")

        assert response.status_code in [200, 204]

        # Verificar que el departamento ya no existe
        print("🔍 Verificando que el departamento fue eliminado")
        response_get = requests.get(f"{DEPARTAMENTOS_URL}/departamentos/{dept_id}")
        assert response_get.status_code == 404

        print("✅ Departamento eliminado exitosamente")

    @classmethod
    def teardown_class(cls):
        """Limpieza después de ejecutar los tests"""
        print("\n" + "=" * 80)
        print("TESTS COMPLETADOS")
        print("=" * 80)


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v", "-s"])

