# 📋 Resumen de Cambios - Tests del Sistema

## ✅ Archivos Creados

### 📂 tests-sistema/ (nuevo directorio)

1. **README.md**
   - Documentación general del sistema de tests
   - Descripción del flujo de prueba
   - Estructura de archivos

2. **requirements.txt**
   - Dependencias Python necesarias:
     - pytest==8.0.0
     - requests==2.31.0
     - python-dotenv==1.0.1

3. **test_system_integration.py**
   - Tests de integración end-to-end
   - 10 tests que cubren todo el flujo:
     ✓ Crear departamento
     ✓ Crear empleado asociado
     ✓ Verificar empleado existe
     ✓ Validar rechazo de departamento inexistente
     ✓ Listar empleados y departamentos
     ✓ Actualizar empleado
     ✓ Verificar caché Redis
     ✓ Eliminar empleado y departamento

4. **run_tests.ps1**
   - Script de PowerShell para ejecutar tests automáticamente
   - Verifica que los servicios estén corriendo
   - Crea entorno virtual
   - Instala dependencias
   - Ejecuta tests con pytest

5. **GUIA_EJECUCION.md**
   - Guía completa paso a paso
   - Requisitos previos
   - Comandos de ejecución
   - Solución de problemas
   - Comandos útiles de Docker

6. **COMANDOS_CURL.md**
   - Comandos curl para pruebas manuales
   - Versiones en bash y PowerShell
   - Script PowerShell completo para ejecutar todo el flujo

## ⚙️ Archivos Modificados

### 1. docker-compose.yml
**Cambios:**
- ✅ Agregado servicio RabbitMQ con management UI
- ✅ Configuración de variables de entorno para RabbitMQ en empleados-service
- ✅ Corrección del healthcheck de empleados-service (`/v3/api-docs`)
- ✅ Agregado `start_period` a los healthchecks
- ✅ Configuración de dependencias con conditions

**Configuración RabbitMQ:**
```yaml
rabbitmq:
  image: rabbitmq:3-management
  ports:
    - "5672:5672"   # AMQP
    - "15672:15672" # Management UI
```

### 2. gestion-empleados/src/main/resources/application.yml
**Cambios:**
- ✅ Agregada configuración de RabbitMQ:
```yaml
spring:
  rabbitmq:
    host: ${SPRING_RABBITMQ_HOST:localhost}
    port: ${SPRING_RABBITMQ_PORT:5672}
    username: ${SPRING_RABBITMQ_USERNAME:guest}
    password: ${SPRING_RABBITMQ_PASSWORD:guest}
```

## 🎯 Cómo Ejecutar los Tests

### Paso 1: Levantar Servicios
```powershell
# Desde la raíz del proyecto
docker-compose up --build
```

**Espera a ver:**
- ✅ `departamentos | INFO: Uvicorn running on http://0.0.0.0:8081`
- ✅ `empleados-service | Started EmpleadosApplication`
- ✅ `rabbitmq-broker | Server startup complete`
- ✅ `redis-cache | Ready to accept connections`

### Paso 2: Ejecutar Tests Automáticos
```powershell
cd gestion-empleados\tests-sistema
.\run_tests.ps1
```

### Alternativa: Pruebas Manuales
```powershell
# Ver COMANDOS_CURL.md para ejemplos completos
# O usar Swagger UI:
# - Departamentos: http://localhost:8081/docs
# - Empleados: http://localhost:8080/swagger-ui.html
```

## 🔧 Servicios Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Departamentos** | http://localhost:8081 | API REST (FastAPI) |
| **Empleados** | http://localhost:8080 | API REST (Spring Boot) |
| **Redis** | localhost:6379 | Caché y streams |
| **RabbitMQ** | localhost:5672 | Mensajería AMQP |
| **RabbitMQ UI** | http://localhost:15672 | Panel de administración (guest/guest) |
| **Swagger Dept** | http://localhost:8081/docs | Documentación API |
| **Swagger Emp** | http://localhost:8080/swagger-ui.html | Documentación API |

## 📊 Cobertura de Tests

### Tests Implementados (10)

1. **test_01_crear_departamento**
   - Crea departamento "IT"
   - Verifica status 200/201
   - Valida datos de respuesta

2. **test_02_crear_empleado_asociado**
   - Crea empleado "Juan Pérez" en departamento "IT"
   - Verifica status 200/201
   - Valida relación con departamento

3. **test_03_verificar_empleado_existe**
   - Consulta empleado por ID
   - Verifica que existe y datos son correctos

4. **test_04_crear_empleado_departamento_inexistente**
   - Intenta crear empleado con departamento "NOEXISTE"
   - **Debe fallar con error 400**
   - Valida la validación de negocio

5. **test_05_listar_empleados**
   - Obtiene lista de todos los empleados
   - Verifica que el empleado creado está en la lista

6. **test_06_listar_departamentos**
   - Obtiene lista de todos los departamentos
   - Verifica que el departamento creado está en la lista

7. **test_07_actualizar_empleado**
   - Actualiza nombre y email del empleado
   - Verifica que los cambios se guardaron

8. **test_08_verificar_cache_redis**
   - Realiza 2 consultas consecutivas
   - Mide tiempos de respuesta
   - Verifica que la segunda es del caché (más rápida)

9. **test_09_eliminar_empleado**
   - Elimina el empleado
   - Verifica que ya no existe (404)

10. **test_10_eliminar_departamento**
    - Elimina el departamento
    - Verifica que ya no existe (404)

## 🐛 Solución de Problemas Comunes

### Problema: Servicio de empleados no inicia

**Síntomas:**
- Docker logs muestra que Maven está descargando dependencias
- Tarda mucho tiempo

**Solución:**
- Es normal en la primera ejecución
- Maven descarga todas las dependencias (puede tardar 5-10 minutos)
- Espera pacientemente hasta ver "Started EmpleadosApplication"

### Problema: "Connection refused" en tests

**Síntomas:**
- Tests fallan con ConnectionError
- No se puede conectar a localhost:8080 o 8081

**Solución:**
```powershell
# 1. Verificar que los servicios están corriendo
docker-compose ps

# 2. Ver logs para identificar errores
docker-compose logs -f

# 3. Esperar a que los servicios estén completamente iniciados
# Los healthchecks pueden tardar 30-40 segundos
```

### Problema: Test 04 pasa cuando debería fallar

**Síntomas:**
- `test_04_crear_empleado_departamento_inexistente` no falla
- Empleado se crea aunque departamento no existe

**Solución:**
- Verificar que el servicio de empleados valida departamentos
- Revisar logs: `docker-compose logs empleados-service`
- Asegurarse de que `DEPARTAMENTOS_SERVICE_URL` está configurado

### Problema: Caché Redis no funciona (Test 08 falla)

**Síntomas:**
- Ambas consultas tardan lo mismo
- No hay mejora de performance

**Solución:**
```powershell
# Verificar que Redis está corriendo
docker-compose ps redis

# Ver logs de Redis
docker-compose logs redis

# Reiniciar Redis
docker-compose restart redis
```

## 📝 Notas Importantes

1. **Primera Ejecución**: Puede tardar 5-10 minutos en compilar y descargar dependencias

2. **Persistencia de Datos**: 
   - MongoDB: Datos en la nube (MongoDB Atlas)
   - Redis: Volumen local `redis_data`
   - Para limpiar: `docker-compose down -v`

3. **Variables de Entorno**: 
   - Asegúrate de tener el archivo `.env` configurado
   - Debe incluir `MONGODB_URI`, `MONGODB_DATABASE`, `DEP_DATABASE_URL`

4. **Puertos**: 
   - Si los puertos están ocupados, modifica `docker-compose.yml`

5. **Limpieza**:
   ```powershell
   # Detener servicios
   docker-compose down
   
   # Detener y eliminar volúmenes
   docker-compose down -v
   
   # Reconstruir todo desde cero
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up
   ```

## 🎓 Próximos Pasos

Para el Reto 3, deberás agregar:

1. **Servicio de Notificaciones** (Python/Node.js)
   - Consumir eventos de RabbitMQ
   - Enviar notificaciones cuando se crea/actualiza un empleado

2. **Servicio de Perfiles** (Python/Node.js)
   - Gestionar perfiles de usuario
   - Integrar con empleados

3. **Tests de Integración Extendidos**
   - Verificar flujo completo con 4 servicios
   - Validar eventos en RabbitMQ

## 📚 Recursos Adicionales

- **Docker Compose**: https://docs.docker.com/compose/
- **pytest**: https://docs.pytest.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Spring Boot**: https://spring.io/projects/spring-boot
- **RabbitMQ**: https://www.rabbitmq.com/documentation.html

## ✅ Checklist de Verificación

Antes de entregar, verifica que:

- [ ] Los servicios inician correctamente con `docker-compose up --build`
- [ ] Todos los tests pasan con `.\run_tests.ps1`
- [ ] Swagger UI funciona para ambos servicios
- [ ] RabbitMQ Management UI es accesible
- [ ] Los datos persisten después de reiniciar servicios
- [ ] La validación de departamentos inexistentes funciona (test 04)
- [ ] El caché Redis mejora el performance (test 08)

## 🎉 ¡Listo!

Tu sistema de microservicios está completo con:
- ✅ 2 microservicios (Empleados + Departamentos)
- ✅ Redis para caché
- ✅ RabbitMQ para mensajería
- ✅ Tests de integración completos
- ✅ Documentación exhaustiva
- ✅ Scripts de automatización

**¡Felicitaciones! El sistema está listo para probar.** 🚀

