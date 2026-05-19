# Tests del Sistema - Gestión de Empleados

## Descripción
Tests de integración end-to-end para verificar el funcionamiento completo del sistema de microservicios.

## Requisitos
- Python 3.8+
- Servicios levantados con `docker-compose up --build`

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución de Tests

### Windows (PowerShell)
```powershell
.\run_tests.ps1
```

### Linux/Mac
```bash
python -m pytest test_system_integration.py -v
```

## Flujo de Prueba

1. **Crear un departamento**: Verifica que se pueda crear un departamento en el servicio de departamentos
2. **Crear un empleado asociado**: Verifica que se pueda crear un empleado vinculado al departamento
3. **Verificar que el empleado existe**: Consulta el empleado creado
4. **Intentar crear empleado con departamento inexistente**: Verifica que falle con error 400
5. **Verificar persistencia**: Reinicia los contenedores y verifica que los datos persisten

## Estructura de Tests

- `test_system_integration.py`: Tests de integración del sistema completo
- `requirements.txt`: Dependencias de Python necesarias
- `run_tests.ps1`: Script de PowerShell para ejecutar los tests

## Servicios Testeados

- **Departamentos** (FastAPI): http://localhost:8081
- **Empleados** (Spring Boot): http://localhost:8080
- **Redis**: Caché y streams
- **RabbitMQ**: Mensajería entre servicios

