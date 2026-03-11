# 🚀 Quick Start - Tests del Sistema

## ⚡ Inicio Rápido (3 pasos)

### 1. Levantar Servicios
```powershell
docker-compose up --build
```
⏱️ Espera 5-10 minutos la primera vez (Maven descarga dependencias)

### 2. Ejecutar Tests
```powershell
cd gestion-empleados\tests-sistema
.\run_tests.ps1
```

### 3. ✅ Ver Resultados
```
✅ test_01_crear_departamento PASSED
✅ test_02_crear_empleado_asociado PASSED
✅ test_03_verificar_empleado_existe PASSED
✅ test_04_crear_empleado_departamento_inexistente PASSED
✅ test_05_listar_empleados PASSED
✅ test_06_listar_departamentos PASSED
✅ test_07_actualizar_empleado PASSED
✅ test_08_verificar_cache_redis PASSED
✅ test_09_eliminar_empleado PASSED
✅ test_10_eliminar_departamento PASSED

================================
TESTS COMPLETADOS EXITOSAMENTE
================================
```

---

## 📋 Lo que se ha implementado

### ✅ Tests del Sistema (10 tests)
1. ✓ Crear departamento
2. ✓ Crear empleado asociado
3. ✓ Verificar empleado existe  
4. ✓ Validar rechazo de departamento inexistente (debe fallar con 400)
5. ✓ Listar empleados
6. ✓ Listar departamentos
7. ✓ Actualizar empleado
8. ✓ Verificar caché Redis (mejora de performance)
9. ✓ Eliminar empleado
10. ✓ Eliminar departamento

### 📁 Archivos Creados
```
gestion-empleados/tests-sistema/
├── README.md                     # Documentación general
├── GUIA_EJECUCION.md            # Guía paso a paso completa
├── COMANDOS_CURL.md             # Comandos para pruebas manuales
├── RESUMEN_CAMBIOS.md           # Resumen de todos los cambios
├── requirements.txt              # Dependencias Python
├── test_system_integration.py   # Tests de integración
├── run_tests.ps1                # Script de ejecución automática
└── .gitignore
```

### ⚙️ Configuración Actualizada
- ✅ **docker-compose.yml**: Agregado RabbitMQ con management UI
- ✅ **application.yml**: Configuración de RabbitMQ
- ✅ **Healthchecks**: Corregidos para empleados-service

---

## 🌐 URLs de los Servicios

| Servicio | URL | Usuario/Contraseña |
|----------|-----|-------------------|
| **Departamentos API** | http://localhost:8081 | - |
| **Empleados API** | http://localhost:8080 | - |
| **Swagger Departamentos** | http://localhost:8081/docs | - |
| **Swagger Empleados** | http://localhost:8080/swagger-ui.html | - |
| **RabbitMQ Management** | http://localhost:15672 | guest / guest |

---

## 🐛 Troubleshooting Rápido

### Problema: Servicios no inician
```powershell
docker-compose down -v
docker-compose up --build
```

### Problema: Tests fallan
```powershell
# Espera a que los servicios estén completamente iniciados
docker-compose ps
# Todos deben mostrar "healthy"
```

### Problema: Puerto ocupado
```powershell
# Buscar qué usa el puerto
netstat -ano | findstr :8080
# Matar el proceso o cambiar puerto en docker-compose.yml
```

---

## 📚 Documentación Completa

- **GUIA_EJECUCION.md**: Guía completa con solución de problemas
- **COMANDOS_CURL.md**: Ejemplos de pruebas manuales con curl/PowerShell
- **RESUMEN_CAMBIOS.md**: Lista detallada de todos los cambios

---

## ✨ Flujo de Prueba

```
1. Crear Dept IT → 2. Crear Emp Juan → 3. Verificar existe
                                          ↓
4. Intentar Dept inválido (FAIL) ← 5. Listar Empleados
                                          ↓
                            6. Listar Departamentos
                                          ↓
                            7. Actualizar Empleado
                                          ↓
                            8. Verificar Caché Redis
                                          ↓
                       9. Eliminar Empleado
                                          ↓
                      10. Eliminar Departamento
```

---

## 💡 Comandos Útiles

```powershell
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f empleados-service

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Limpiar todo (incluye volúmenes)
docker-compose down -v
```

---

## 🎯 Verificación Rápida

Antes de entregar, verifica:
- [ ] `docker-compose up --build` inicia sin errores
- [ ] `.\run_tests.ps1` pasa todos los tests (10/10)
- [ ] Swagger UI funciona en ambos servicios
- [ ] RabbitMQ Management UI es accesible
- [ ] Test 04 falla correctamente (departamento inexistente → error 400)

---

## 🎉 ¡Listo!

Tu sistema completo incluye:
- ✅ Microservicio Empleados (Java/Spring Boot)
- ✅ Microservicio Departamentos (Python/FastAPI)
- ✅ Redis (Caché)
- ✅ RabbitMQ (Mensajería)
- ✅ 10 Tests de Integración E2E
- ✅ Documentación Completa
- ✅ Scripts de Automatización

**Para ejecutar:** `docker-compose up --build` → `.\run_tests.ps1`

