# Pruebas Unitarias - Gestión de Departamentos

Este directorio contiene las pruebas unitarias para el microservicio de gestión de departamentos.

## Estructura de Pruebas

```
tests/
├── __init__.py
├── conftest.py                    # Configuración y fixtures compartidas
├── test_departamento_service.py   # Pruebas del servicio de departamentos
└── test_departamentos_api.py      # Pruebas de los endpoints de la API
```

## Dependencias de Testing

Las dependencias necesarias para ejecutar las pruebas están en `requirements.txt`:

- **pytest**: Framework de pruebas
- **pytest-cov**: Plugin para cobertura de código
- **pytest-asyncio**: Soporte para pruebas asíncronas
- **httpx**: Cliente HTTP para pruebas de FastAPI

## Instalación

Instalar las dependencias de testing:

```bash
pip install -r requirements.txt
```

## Ejecutar las Pruebas

### Ejecutar todas las pruebas

```bash
pytest
```

### Ejecutar con reporte de cobertura

```bash
pytest --cov=app --cov-report=html
```

Esto generará un reporte HTML en `htmlcov/index.html` que puedes abrir en tu navegador.

### Ejecutar con cobertura en terminal

```bash
pytest --cov=app --cov-report=term-missing
```

### Ejecutar pruebas específicas

```bash
# Ejecutar solo las pruebas del servicio
pytest tests/test_departamento_service.py

# Ejecutar solo las pruebas de la API
pytest tests/test_departamentos_api.py

# Ejecutar una clase de pruebas específica
pytest tests/test_departamento_service.py::TestCreateDepartamento

# Ejecutar una prueba específica
pytest tests/test_departamento_service.py::TestCreateDepartamento::test_create_departamento_exitoso
```

### Ejecutar con más detalle (verbose)

```bash
pytest -v
```

### Ejecutar y mostrar prints

```bash
pytest -s
```

## Descripción de las Pruebas

### test_departamento_service.py

Pruebas unitarias para la capa de servicios:

- **TestCreateDepartamento**: Pruebas para la creación de departamentos
  - Creación exitosa
  - Persistencia en base de datos
  - Creación de múltiples departamentos

- **TestGetDepartamento**: Pruebas para obtener departamentos
  - Obtener departamento existente
  - Manejar departamento no existente
  - Validación de IDs

- **TestListDepartamentos**: Pruebas para listar departamentos
  - Lista vacía
  - Lista con datos
  - Ordenamiento alfabético
  - Casos edge

### test_departamentos_api.py

Pruebas unitarias para los endpoints de la API:

- **TestPostDepartamento**: Pruebas del endpoint POST /departamentos
  - Creación exitosa
  - Validación de campos requeridos
  - Validación de longitud de campos
  - Manejo de errores

- **TestGetDepartamentoById**: Pruebas del endpoint GET /departamentos/{dep_id}
  - Obtener departamento existente
  - Manejo de 404 para departamentos no existentes
  - Caracteres especiales en IDs

- **TestGetDepartamentos**: Pruebas del endpoint GET /departamentos
  - Listar departamentos vacíos
  - Listar con datos
  - Verificar ordenamiento
  - Persistencia entre llamadas

- **TestIntegracionCompleta**: Pruebas de flujos completos
  - Flujo CRUD completo
  - Creación y listado de múltiples departamentos

## Fixtures Disponibles

Definidas en `conftest.py`:

- **db_session**: Sesión de base de datos de pruebas (SQLite en memoria)
- **client**: Cliente de pruebas de FastAPI
- **departamento_data**: Datos de ejemplo para un departamento
- **departamento_data_2**: Segundo conjunto de datos de ejemplo
- **departamento_data_list**: Lista de múltiples departamentos de ejemplo

## Configuración

La configuración de pytest está en `pytest.ini` e incluye:

- Opciones de salida verbose
- Marcadores personalizados (unit, integration, slow)
- Configuración de cobertura
- Patrones de búsqueda de pruebas

## Buenas Prácticas

1. **Nomenclatura**: Los archivos de prueba comienzan con `test_`
2. **Organización**: Las pruebas están organizadas en clases por funcionalidad
3. **Patrón AAA**: Cada prueba sigue el patrón Arrange-Act-Assert
4. **Aislamiento**: Cada prueba es independiente y usa fixtures limpias
5. **Cobertura**: Apunta a >80% de cobertura de código

## Ejemplo de Salida

```
================================================ test session starts ================================================
collected 25 items

tests/test_departamento_service.py::TestCreateDepartamento::test_create_departamento_exitoso PASSED          [  4%]
tests/test_departamento_service.py::TestCreateDepartamento::test_create_departamento_persiste_en_db PASSED   [  8%]
...
tests/test_departamentos_api.py::TestIntegracionCompleta::test_flujo_completo_crud PASSED                    [100%]

================================================ 25 passed in 2.34s =================================================
```

## Comandos Útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar todas las pruebas con cobertura
pytest --cov=app --cov-report=term-missing

# Ejecutar pruebas en modo watch (requiere pytest-watch)
ptw

# Generar reporte HTML de cobertura
pytest --cov=app --cov-report=html && start htmlcov/index.html
```
