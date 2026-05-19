# Guía Rápida - Pruebas del Sistema (Java/Spring Boot)

## ⚡ Ejecución Rápida

### Desde la carpeta gestion-empleados:

```powershell
# Compilar y ejecutar pruebas de integración
mvn test -Dtest=SystemIntegrationTest

# Con output detallado
mvn test -Dtest=SystemIntegrationTest -X

# Solo compilar sin ejecutar tests
mvn compile -Dmaven.test.skip=true
```

## 📋 Pre-requisitos

1. **Servicios activos:**
```powershell
# Desde la raíz del proyecto
docker-compose up --build -d
```

2. **Esperar ~30 segundos** para que los servicios inicien

## 🧪 Ejecutar desde IDE

### IntelliJ IDEA / VS Code:
1. Abrir: `src/test/java/com/microservicios/empleados/integration/SystemIntegrationTest.java`
2. Click derecho → "Run SystemIntegrationTest"  
3. Ver resultados en la pestaña de Test

## 🔍 Verificar servicios manualmente

```bash
# Verificar que los servicios responden
curl http://localhost:8080/docs  # Empleados
curl http://localhost:8081/docs  # Departamentos

# Probar endpoints
curl -X GET http://localhost:8080/empleados
curl -X GET http://localhost:8081/departamentos
```

## 📊 Resultado Esperado

```
Tests run: 4, Failures: 0, Errors: 0, Skipped: 0

[INFO] BUILD SUCCESS
```

## 🐛 Solución Rápida de Problemas

### Error: "Los servicios no están disponibles"
```powershell
docker-compose ps          # Ver estado
docker-compose restart     # Reiniciar
docker-compose logs -f     # Ver logs
```

### Error de compilación Maven
```powershell
mvn clean compile          # Limpiar y recompilar
mvn dependency:resolve     # Resolver dependencias
```

### Servicios en otros puertos
```powershell
# Configurar URLs personalizadas
$env:EMPLEADOS_URL="http://localhost:8080"
$env:DEPARTAMENTOS_URL="http://localhost:8081"
mvn test -Dtest=SystemIntegrationTest
```

## 📝 Pruebas incluidas

✅ **Test 1:** Crear empleado con departamento válido
✅ **Test 2:** Verificar que empleado existe  
✅ **Test 3:** Rechazar empleado con departamento inexistente (400)
✅ **Test 4:** Listar empleados

**Prerequisito (automático):** Crear departamento "IT"

## 📚 Más información

Ver documentación completa: [src/test/java/com/microservicios/empleados/integration/README.md](src/test/java/com/microservicios/empleados/integration/README.md)

---

**Tip:** Para ejecutar un solo test: `mvn test -Dtest=SystemIntegrationTest#test1_crearEmpleadoValido`
