# Guía de Ejecución - Tests del Sistema

## 📋 Requisitos Previos

1. **Docker y Docker Compose** instalados
2. **Python 3.8+** instalado
3. **Variables de entorno** configuradas en el archivo `.env` en la raíz del proyecto

## 🚀 Paso 1: Levantar los Servicios

Desde la raíz del proyecto (`microservicios/`), ejecuta:

```powershell
docker-compose up --build
```

Este comando:
- Construirá las imágenes de los microservicios
- Levantará Redis, RabbitMQ, el servicio de departamentos y el servicio de empleados
- Puede tardar varios minutos la primera vez

**Espera a que veas estos mensajes:**
- ✅ `departamentos | INFO: Uvicorn running on http://0.0.0.0:8081`
- ✅ `empleados-service | Started EmpleadosApplication in X seconds`
- ✅ `rabbitmq-broker | Server startup complete`
- ✅ `redis-cache | Ready to accept connections`

## 🧪 Paso 2: Ejecutar los Tests

### Opción 1: Usando el Script de PowerShell (Recomendado)

```powershell
cd gestion-empleados\tests-sistema
.\run_tests.ps1
```

### Opción 2: Manual

```powershell
cd gestion-empleados\tests-sistema

# Crear entorno virtual (solo la primera vez)
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python -m pytest test_system_integration.py -v -s
```

## 📊 Tests Incluidos

Los tests verifican el siguiente flujo:

1. ✅ **Crear Departamento**: `POST /departamentos`
2. ✅ **Crear Empleado**: `POST /empleados` (con departamento válido)
3. ✅ **Obtener Empleado**: `GET /empleados/{id}`
4. ✅ **Crear Empleado Inválido**: `POST /empleados` (con departamento inexistente - debe fallar)
5. ✅ **Listar Empleados**: `GET /empleados`
6. ✅ **Listar Departamentos**: `GET /departamentos`
7. ✅ **Actualizar Empleado**: `PUT /empleados/{id}`
8. ✅ **Verificar Caché Redis**: Múltiples consultas para verificar mejora de performance
9. ✅ **Eliminar Empleado**: `DELETE /empleados/{id}`
10. ✅ **Eliminar Departamento**: `DELETE /departamentos/{id}`

## 📝 Ejemplo de Salida Esperada

```
================================
TESTS DEL SISTEMA - Microservicios
================================

Verificando servicios Docker...
Servicios encontrados:
empleados-service   Up 2 minutes
departamentos       Up 2 minutes
redis-cache         Up 2 minutes
rabbitmq-broker     Up 2 minutes

Ejecutando tests...

test_01_crear_departamento PASSED
test_02_crear_empleado_asociado PASSED
test_03_verificar_empleado_existe PASSED
test_04_crear_empleado_departamento_inexistente PASSED
test_05_listar_empleados PASSED
test_06_listar_departamentos PASSED
test_07_actualizar_empleado PASSED
test_08_verificar_cache_redis PASSED
test_09_eliminar_empleado PASSED
test_10_eliminar_departamento PASSED

================================
TESTS COMPLETADOS EXITOSAMENTE
================================
```

## 🐛 Solución de Problemas

### Error: "Los servicios no están corriendo"

**Solución:** Asegúrate de haber levantado los servicios con `docker-compose up --build`

### Error: "Connection refused" o "Service unavailable"

**Solución:** Los servicios pueden tardar en iniciar. Espera 1-2 minutos y vuelve a intentar.

Verifica el estado:
```powershell
docker-compose ps
```

### Error: "Department not found" al crear empleado

**Solución:** Este es el comportamiento esperado para `test_04`. Asegúrate de que el servicio de empleados esté validando los departamentos correctamente.

### El servicio de empleados no inicia

**Solución:** 
1. Verifica los logs: `docker-compose logs empleados-service`
2. Asegúrate de tener las variables de entorno correctas en `.env`
3. Verifica que MongoDB Atlas sea accesible

## 🔍 Verificación Manual

Puedes probar los endpoints manualmente:

### Swagger UI - Departamentos
http://localhost:8081/docs

### Swagger UI - Empleados  
http://localhost:8080/swagger-ui.html

### RabbitMQ Management
http://localhost:15672 (usuario: guest, password: guest)

## 📦 Comandos Útiles

```powershell
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f empleados-service

# Reiniciar los servicios
docker-compose restart

# Detener los servicios
docker-compose down

# Detener y eliminar volúmenes (datos persistentes)
docker-compose down -v

# Ver el estado de los servicios
docker-compose ps
```

## 🎯 Verificación de Persistencia

Para verificar que los datos persisten después de reiniciar:

1. Crea algunos empleados y departamentos
2. Detén los servicios: `docker-compose down`
3. Vuelve a levantar: `docker-compose up`
4. Verifica que los datos siguen ahí con los tests

**Nota:** Los datos de MongoDB y Redis persisten en volúmenes de Docker.

## 📚 Estructura de los Tests

```
tests-sistema/
├── README.md                      # Documentación general
├── GUIA_EJECUCION.md             # Esta guía
├── requirements.txt               # Dependencias Python
├── run_tests.ps1                 # Script de ejecución
└── test_system_integration.py    # Tests de integración
```

## 🔄 Flujo de Prueba Completo

```
┌─────────────────────────────────────────────────────┐
│  1. Crear Departamento IT                           │
│     POST /departamentos                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  2. Crear Empleado Juan Pérez (Dept: IT)           │
│     POST /empleados                                 │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  3. Verificar Empleado Existe                       │
│     GET /empleados/E001                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  4. Intentar Crear Empleado con Dept Inválido      │
│     POST /empleados (departamentoId: NOEXISTE)     │
│     Esperado: ERROR 400                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  5-6. Listar Empleados y Departamentos              │
│     GET /empleados                                  │
│     GET /departamentos                              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  7. Actualizar Empleado                             │
│     PUT /empleados/E001                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  8. Verificar Caché Redis (2 consultas)            │
│     GET /empleados/E001 (x2)                        │
│     Segunda debe ser más rápida                     │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  9-10. Limpiar: Eliminar Empleado y Departamento   │
│     DELETE /empleados/E001                          │
│     DELETE /departamentos/IT                        │
└─────────────────────────────────────────────────────┘
```

## 💡 Consejos

- **Primera ejecución**: Los servicios pueden tardar más en compilar (especialmente Java/Maven)
- **Limpieza**: Si tienes problemas, intenta `docker-compose down -v && docker-compose up --build`
- **Desarrollo**: Puedes mantener los servicios corriendo y ejecutar los tests múltiples veces
- **Debugging**: Usa `docker-compose logs -f [servicio]` para ver logs en tiempo real

