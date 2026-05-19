# Pruebas del Sistema - Microservicios

Este directorio contiene las pruebas de integración end-to-end del sistema completo de gestión de departamentos y empleados.

## 📁 Estructura

```
tests-sistema/
├── __init__.py
├── requirements.txt                  # Dependencias para las pruebas
├── test_system_integration.py        # Script Python automatizado
├── run_tests.ps1                     # Script PowerShell para pruebas manuales
└── README.md                         # Esta documentación
```

## 🎯 Objetivo

Verificar el funcionamiento completo del sistema de microservicios, incluyendo:

- ✅ Comunicación entre servicios (Empleados ↔ Departamentos)
- ✅ Validación de datos entre servicios
- ✅ Persistencia de datos
- ✅ Manejo de errores
- ✅ APIs REST funcionando correctamente

## 🚀 Flujo de Pruebas

Las pruebas siguen este flujo:

1. **Verificar disponibilidad**: Comprobar que todos los servicios estén activos
2. **Crear departamento**: Crear departamento "IT" (Tecnología)
3. **Crear empleado válido**: Crear empleado "E001" asociado al departamento "IT"
4. **Verificar empleado**: Comprobar que el empleado existe con GET
5. **Validar departamento inexistente**: Intentar crear empleado con departamento inválido (debe fallar con 400)
6. **Listar recursos**: Listar todos los departamentos y empleados
7. **Limpieza**: Eliminar datos de prueba creados

## 📋 Pre-requisitos

### Servicios activos

Los servicios deben estar ejecutándose:

```powershell
# Desde la raíz del proyecto
docker-compose up --build
```

Esto inicia:
- **Departamentos**: http://localhost:8081
- **Empleados**: http://localhost:8080
- **Redis**: localhost:6379
- **PostgreSQL**: (Supabase Cloud)
- **MongoDB**: (MongoDB Atlas Cloud)

### Dependencias Python

Para ejecutar el script Python:

```powershell
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r tests-sistema/requirements.txt
```

## 🧪 Ejecutar las Pruebas

### Opción 1: Script Python Automatizado (Recomendado)

El script Python proporciona pruebas automatizadas con output colorizado:

```powershell
# Ejecutar todas las pruebas
python gestion-Departamentos/tests-sistema/test_system_integration.py

# Con URLs personalizadas
python gestion-Departamentos/tests-sistema/test_system_integration.py `
    --departamentos-url http://localhost:8081 `
    --empleados-url http://localhost:8080

# Sin limpieza de datos al final
python gestion-Departamentos/tests-sistema/test_system_integration.py --no-cleanup
```

**Características:**
- ✅ Verificación automática de disponibilidad de servicios
- ✅ Ejecución secuencial de todas las pruebas
- ✅ Output colorizado y estructurado
- ✅ Resumen de resultados
- ✅ Exit code apropiado (0 = éxito, 1 = fallos)

### Opción 2: Script PowerShell

Para pruebas manuales con control detallado:

```powershell
# Ejecutar pruebas
.\gestion-Departamentos\tests-sistema\run_tests.ps1

# Iniciar servicios y ejecutar pruebas
.\gestion-Departamentos\tests-sistema\run_tests.ps1 -Build

# Sin limpieza automática
.\gestion-Departamentos\tests-sistema\run_tests.ps1 -SkipCleanup

# Con URLs personalizadas
.\gestion-Departamentos\tests-sistema\run_tests.ps1 `
    -DepartamentosUrl "http://localhost:8081" `
    -EmpleadosUrl "http://localhost:8080"
```

**Parámetros disponibles:**
- `-Build`: Inicia docker-compose antes de las pruebas
- `-SkipCleanup`: No elimina datos de prueba al finalizar
- `-DepartamentosUrl`: URL del servicio de departamentos
- `-EmpleadosUrl`: URL del servicio de empleados

### Opción 3: Pruebas Manuales con cURL

#### 1. Crear un departamento

```bash
curl -X POST http://localhost:8081/departamentos \
  -H "Content-Type: application/json" \
  -d '{"id": "IT", "nombre": "Tecnología", "descripcion": "Departamento de TI"}'
```

**Respuesta esperada:** Status 200/201 con datos del departamento creado

#### 2. Crear empleado asociado

```bash
curl -X POST http://localhost:8080/empleados \
  -H "Content-Type: application/json" \
  -d '{"id": "E001", "nombre": "Juan Pérez", "email": "juan@empresa.com", "departamentoId": "IT"}'
```

**Respuesta esperada:** Status 200/201 con datos del empleado creado

#### 3. Verificar empleado

```bash
curl -X GET http://localhost:8080/empleados/E001
```

**Respuesta esperada:** Status 200 con datos del empleado

#### 4. Intentar crear empleado con departamento inexistente

```bash
curl -X POST http://localhost:8080/empleados \
  -H "Content-Type: application/json" \
  -d '{"id": "E002", "nombre": "María López", "email": "maria@empresa.com", "departamentoId": "DEPT_NO_EXISTE"}'
```

**Respuesta esperada:** Status 400 con mensaje de error

#### 5. Listar recursos

```bash
# Listar departamentos
curl -X GET http://localhost:8081/departamentos

# Listar empleados
curl -X GET http://localhost:8080/empleados
```

## 📊 Interpretación de Resultados

### Pruebas Exitosas

```
✓ Departamento creado exitosamente (Status: 201)
✓ Empleado creado exitosamente (Status: 201)
✓ Empleado encontrado: Juan Pérez
✓ Validación correcta: rechazado con status 400
✓ Encontrados 1 departamento(s)
✓ Encontrados 1 empleado(s)

Total de pruebas: 6
Exitosas: 6
Fallidas: 0
Tasa de éxito: 100.0%
```

### Ejemplo de Fallo

```
✗ Error al crear empleado (Status: 500)
  ℹ Error: Internal Server Error

Total de pruebas: 6
Exitosas: 5
Fallidas: 1
Tasa de éxito: 83.3%
```

## 🔍 Prueba de Persistencia

Para verificar que los datos persisten después de reiniciar:

```powershell
# 1. Crear datos
python gestion-Departamentos/tests-sistema/test_system_integration.py --no-cleanup

# 2. Reiniciar contenedores
docker-compose restart

# 3. Verificar que los datos siguen existiendo
curl -X GET http://localhost:8080/empleados/E001
curl -X GET http://localhost:8081/departamentos/IT
```

**Resultado esperado:** Los datos deben persistir debido a:
- PostgreSQL (Supabase Cloud) para departamentos
- MongoDB (Atlas Cloud) para empleados
- Redis mantiene caché temporal

## 🐛 Solución de Problemas

### Servicios no disponibles

**Síntoma:** "Servicio no disponible después de N intentos"

**Soluciones:**
```powershell
# Verificar que docker-compose está ejecutándose
docker-compose ps

# Ver logs de los servicios
docker-compose logs departamentos
docker-compose logs empleados-service

# Reiniciar servicios
docker-compose restart

# Reconstruir desde cero
docker-compose down
docker-compose up --build
```

### Error 400 al crear empleado válido

**Síntoma:** Error 400 al crear empleado con departamento que debería existir

**Posibles causas:**
1. El departamento no se creó correctamente
2. Problemas de comunicación entre servicios
3. Redis no está disponible

**Verificación:**
```bash
# Verificar que el departamento existe
curl http://localhost:8081/departamentos/IT

# Ver logs del servicio de empleados
docker-compose logs empleados-service

# Verificar conectividad con Redis
docker exec -it redis-cache redis-cli ping
```

### Timeout en las peticiones

**Síntoma:** "Timeout after 10 seconds"

**Soluciones:**
```powershell
# Verificar salud de los servicios
docker-compose ps

# Ver uso de recursos
docker stats

# Reiniciar servicios problem áticos
docker-compose restart empleados-service departamentos
```

### Datos no persisten

**Síntoma:** Datos desaparecen al reiniciar

**Verificar:**
1. Conexión a bases de datos cloud (MongoDB Atlas, Supabase)
2. Variables de entorno en `.env`
3. Estado de las bases de datos cloud

```powershell
# Ver variables de entorno cargadas
docker-compose config

# Verificar logs de conexión a BD
docker-compose logs | Select-String "database|mongodb|postgres"
```

## 📝 Notas Adicionales

### Limpieza Manual de Datos

Si necesitas limpiar datos manualmente:

```bash
# Eliminar empleado
curl -X DELETE http://localhost:8080/empleados/E001

# Eliminar departamento
curl -X DELETE http://localhost:8081/departamentos/IT
```

### Acceder a la Documentación de las APIs

- **Departamentos**: http://localhost:8081/docs
- **Empleados**: http://localhost:8080/docs

### Ejecutar con Pytest

También puedes ejecutar como prueba de pytest:

```powershell
pytest gestion-Departamentos/tests-sistema/test_system_integration.py -v
```

## 🎓 Reglas de Validación Probadas

1. ✅ **Departamento debe existir**: No se puede crear empleado con departamento inexistente
2. ✅ **Comunicación entre servicios**: Empleados valida departamentos llamando al servicio de Departamentos
3. ✅ **Caché funcional**: Redis cachea respuestas de departamentos
4. ✅ **Persistencia**: Datos persisten en bases de datos cloud
5. ✅ **APIs REST**: Todos los endpoints responden correctamente
6. ✅ **Manejo de errores**: Errores retornan códigos HTTP apropiados

## 🔗 Referencias

- [Docker Compose](../../../docker-compose.yml)
- [Documentación Departamentos](https://localhost:8081/docs)
- [Documentación Empleados](http://localhost:8080/docs)
- [Pruebas Unitarias Departamentos](../tests/)

---

**Última actualización:** Marzo 2026
