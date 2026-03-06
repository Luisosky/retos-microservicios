# Pruebas del Sistema - Gestión de Empleados

Este directorio contiene las pruebas de integración end-to-end del sistema desde la perspectiva del microservicio de empleados (Java/Spring Boot).

## 📁 Estructura

```
src/test/java/com/microservicios/empleados/integration/
└── SystemIntegrationTest.java    # Pruebas de integración con JUnit 5
```

## 🎯 Objetivo

Verificar el funcionamiento del servicio de empleados, incluyendo:

- ✅ CRUD de empleados
- ✅ Validación de departamentos existentes
- ✅ Validación de rechazo de departamentos inexistentes (Status 400)
- ✅ Persistencia de datos en MongoDB Atlas
- ✅ Comunicación con el servicio de departamentos
- ✅ APIs REST funcionando correctamente

## 🚀 Flujo de Pruebas

Las pruebas siguen este flujo:

1. **Verificar disponibilidad**: Comprobar que todos los servicios estén activos
2. **Crear departamento prerequisito**: El departamento "IT" se crea automáticamente como prerequisito (no es un test)
3. **Test 1 - Crear empleado válido**: Crear empleado "E001" con departamento "IT"
4. **Test 2 - Verificar empleado**: Comprobar que el empleado existe con GET
5. **Test 3 - Rechazar departamento inexistente**: Intentar crear empleado con departamento inválido (debe fallar con 400)
6. **Test 4 - Listar empleados**: Listar todos los empleados
7. **Limpieza**: Eliminar datos de prueba de empleados

## 📋 Pre-requisitos

### 1. Servicios activos

Los servicios deben estar ejecutándose:

```powershell
# Desde la raíz del proyecto (microservicios/)
docker-compose up --build
```

Esto inicia:
- **Empleados (Java/Spring Boot)**: http://localhost:8080
- **Departamentos (Python/FastAPI)**: http://localhost:8081
- **Redis**: localhost:6379
- **MongoDB Atlas**: (Cloud - configurado en .env)
- **PostgreSQL Supabase**: (Cloud - configurado en .env)

### 2. Java y Maven

Asegúrate de tener instalado:
- Java 17 o superior
- Maven 3.6 o superior

```powershell
# Verificar instalación
java -version
mvn -version
```

## 🧪 Ejecutar las Pruebas

### Opción 1: Maven (Recomendado)

```powershell
# Desde la carpeta gestion-empleados/
cd gestion-empleados

# Ejecutar solo las pruebas de integración
mvn test -Dtest=SystemIntegrationTest

# Ejecutar todas las pruebas
mvn test

# Con output detallado (debug)
mvn test -Dtest=SystemIntegrationTest -X
```

### Opción 2: Desde IDE (IntelliJ IDEA / VS Code)

1. Abrir el archivo `SystemIntegrationTest.java`
2. Click derecho en la clase o método de prueba
3. Seleccionar "Run 'SystemIntegrationTest'" o "Debug"

### Opción 3: Maven con variables de entorno personalizadas

```powershell
# Con URLs no estándar
$env:DEPARTAMENTOS_URL="http://localhost:8081"
$env:EMPLEADOS_URL="http://localhost:8080"
mvn test -Dtest=SystemIntegrationTest
```

## 📊 Interpretación de Resultados

### Pruebas Exitosas

```
-------------------------------------------------------
 T E S T S
-------------------------------------------------------
Running com.microservicios.empleados.integration.SystemIntegrationTest

========================================================================
VERIFICANDO DISPONIBILIDAD DE SERVICIOS
========================================================================

[TEST] Esperando servicio Departamentos...
✓ Servicio Departamentos disponible
[TEST] Esperando servicio Empleados...
✓ Servicio Empleados disponible

========================================================================
CREANDO DEPARTAMENTO PREREQUISITO
========================================================================

[TEST] Crear departamento prerequisito 'IT'...
✓ Departamento prerequisito creado (Status: 201)

========================================================================
TEST 1: CREAR EMPLEADO CON DEPARTAMENTO VÁLIDO
========================================================================

[TEST] Crear empleado...
✓ Empleado creado exitosamente (Status: 201)
  ℹ Respuesta: {"id":"E001",...}

[... más tests ...]

Tests run: 4, Failures: 0, Errors: 0, Skipped: 0

[INFO] BUILD SUCCESS
```

### Ejemplo de Fallo

```
Tests run: 4, Failures: 1, Errors: 0, Skipped: 0

[ERROR] test1_crearEmpleadoValido  Time elapsed: 0.5 s  <<< FAILURE!
java.lang.AssertionError: Empleado debe crearse exitosamente con departamento válido
Expected: <true>
Actual: <false>

[INFO] BUILD FAILURE
```

## 🔍 Prueba de Persistencia

Para verificar que los datos persisten después de reiniciar:

```powershell
# 1. Ejecutar pruebas sin limpieza (comentar @AfterAll en el código)
# 2. Reiniciar contenedores
docker-compose restart

# 3. Verificar que los datos siguen existiendo
curl http://localhost:8080/empleados/E001
curl http://localhost:8081/departamentos/IT

# Resultado esperado: Los datos deben retornarse (Status 200)
```

## 🐛 Solución de Problemas

### Error: "Los servicios no están disponibles"

**Solución:**
```powershell
# Verificar que docker-compose está ejecutándose
docker-compose ps

# Ver logs
docker-compose logs -f empleados-service
docker-compose logs -f departamentos

# Reiniciar servicios
docker-compose restart
```

### Error: "Connection refused"

**Posibles causas:**
1. Los servicios no están ejecutándose
2. Puertos incorrectos (8080, 8081)
3. Firewall bloqueando conexiones

**Solución:**
```powershell
# Verificar que los puertos están escuchando
netstat -ano | findstr :8080
netstat -ano | findstr :8081

# Ver logs de contenedores
docker-compose logs empleados-service
```

### Error de compilación Maven

```powershell
# Limpiar y recompilar
mvn clean compile

# Actualizar dependencias
mvn clean install -U

# Verificar que Java está en PATH
java -version
javac -version
```

### Tests pasan localmente pero fallan en CI/CD

**Causa:** Diferencias en tiempos de espera o configuración

**Solución:** Aumentar el tiempo de espera:
```java
// En SystemIntegrationTest.java, método setup():
boolean departamentosReady = waitForService("Departamentos", DEPARTAMENTOS_URL + "/docs", 60); // Aumentar a 60
```

## 📝 Configuración Adicional

### Variables de Entorno

Puedes configurar las URLs de los servicios:

```powershell
# PowerShell
$env:DEPARTAMENTOS_URL="http://localhost:8081"
$env:EMPLEADOS_URL="http://localhost:8080"

# Bash/Linux
export DEPARTAMENTOS_URL="http://localhost:8081"
export EMPLEADOS_URL="http://localhost:8080"
```

### Ejecutar sin limpieza automática

Comenta la anotación `@AfterAll` en `SystemIntegrationTest.java`:

```java
// @AfterAll
static void tearDown() {
    // ...
}
```

### Agregar más pruebas

Agrega nuevos métodos de prueba siguiendo el patrón:

```java
@Test
@Order(5)
@DisplayName("Test 5: Mi nueva prueba")
void test5_miNuevaPrueba() {
    printHeader("TEST 5: MI NUEVA PRUEBA");
    
    // Tu código de prueba aquí
    
    printSuccess("Prueba exitosa");
}
```

## 🎓 Reglas de Validación Testadas

1. ✅ **Crear empleado con departamento válido**: Status 200/201
2. ✅ **Verificar que empleado existe**: Status 200, datos correctos
3. ✅ **Rechazar departamento inexistente**: Status 400 (Bad Request)
4. ✅ **Listar empleados**: Status 200, array con empleados
5. ✅ **Persistencia en MongoDB**: Datos persisten entre reinicios
6. ✅ **Validación de datos**: Campos correctos en respuesta

## 🔗 Referencias

- [Configuración Maven (pom.xml)](../../pom.xml)
- [Docker Compose](../../../docker-compose.yml)
- [Spring Boot Testing Guide](https://spring.io/guides/gs/testing-web/)
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [TestRestTemplate Docs](https://spring.io/blog/2017/07/05/junit-5-spring-and-spock)

## 💡 Tips

- Usa `mvn test -Dtest=SystemIntegrationTest#test1_crearEmpleadoValido` para ejecutar un test específico
- Agrega `-Dmaven.test.skip=true` para compilar sin ejecutar tests
- Usa IntelliJ IDEA para debugging interactivo
- Los tests están ordenados con `@Order` para ejecución secuencial

## 📌 Notas Importantes

- **El departamento se crea automáticamente** en la fase `@BeforeAll`, no es una prueba
- Las pruebas solo testean el servicio de **EMPLEADOS**
- El servicio de departamentos tiene sus propias pruebas en Python
- La comunicación entre servicios se valida solo desde el lado de empleados

---

**Última actualización:** Marzo 2026
