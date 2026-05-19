# Comandos Curl - Pruebas Manuales del Sistema

Este archivo contiene los comandos curl para probar manualmente el flujo completo del sistema.

## 1️⃣ Crear un Departamento

```bash
curl -X POST http://localhost:8081/departamentos \
  -H "Content-Type: application/json" \
  -d '{
    "id": "IT",
    "nombre": "Tecnología",
    "descripcion": "Departamento de TI"
  }'
```

**PowerShell:**
```powershell
$body = @{
    id = "IT"
    nombre = "Tecnología"
    descripcion = "Departamento de TI"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8081/departamentos" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## 2️⃣ Crear un Empleado Asociado al Departamento

```bash
curl -X POST http://localhost:8080/empleados \
  -H "Content-Type: application/json" \
  -d '{
    "id": "E001",
    "nombre": "Juan Pérez",
    "email": "juan@empresa.com",
    "departamentoId": "IT"
  }'
```

**PowerShell:**
```powershell
$body = @{
    id = "E001"
    nombre = "Juan Pérez"
    email = "juan@empresa.com"
    departamentoId = "IT"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/empleados" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## 3️⃣ Verificar que el Empleado Existe

```bash
curl -X GET http://localhost:8080/empleados/E001
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/empleados/E001" -Method Get
```

## 4️⃣ Intentar Crear Empleado con Departamento Inexistente (Debe Fallar)

```bash
curl -X POST http://localhost:8080/empleados \
  -H "Content-Type: application/json" \
  -d '{
    "id": "E002",
    "nombre": "María García",
    "email": "maria@empresa.com",
    "departamentoId": "NOEXISTE"
  }'
```

**PowerShell:**
```powershell
$body = @{
    id = "E002"
    nombre = "María García"
    email = "maria@empresa.com"
    departamentoId = "NOEXISTE"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8080/empleados" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
} catch {
    Write-Host "Error esperado: $($_.Exception.Message)" -ForegroundColor Yellow
}
```

**Resultado Esperado:** Error 400 - Departamento no encontrado

## 5️⃣ Listar Todos los Empleados

```bash
curl -X GET http://localhost:8080/empleados
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/empleados" -Method Get | ConvertTo-Json
```

## 6️⃣ Listar Todos los Departamentos

```bash
curl -X GET http://localhost:8081/departamentos
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8081/departamentos" -Method Get | ConvertTo-Json
```

## 7️⃣ Actualizar un Empleado

```bash
curl -X PUT http://localhost:8080/empleados/E001 \
  -H "Content-Type: application/json" \
  -d '{
    "id": "E001",
    "nombre": "Juan Pérez Actualizado",
    "email": "juan.actualizado@empresa.com",
    "departamentoId": "IT"
  }'
```

**PowerShell:**
```powershell
$body = @{
    id = "E001"
    nombre = "Juan Pérez Actualizado"
    email = "juan.actualizado@empresa.com"
    departamentoId = "IT"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/empleados/E001" `
    -Method Put `
    -ContentType "application/json" `
    -Body $body
```

## 8️⃣ Obtener Información de un Departamento

```bash
curl -X GET http://localhost:8081/departamentos/IT
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8081/departamentos/IT" -Method Get
```

## 9️⃣ Eliminar un Empleado

```bash
curl -X DELETE http://localhost:8080/empleados/E001
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/empleados/E001" -Method Delete
```

## 🔟 Eliminar un Departamento

```bash
curl -X DELETE http://localhost:8081/departamentos/IT
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8081/departamentos/IT" -Method Delete
```

---

## 🚀 Script PowerShell Completo

Copia y ejecuta este script completo en PowerShell:

```powershell
Write-Host "================================" -ForegroundColor Cyan
Write-Host "PRUEBA MANUAL DEL SISTEMA" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Crear Departamento
Write-Host "1. Creando departamento IT..." -ForegroundColor Yellow
$dept = @{
    id = "IT"
    nombre = "Tecnología"
    descripcion = "Departamento de TI"
} | ConvertTo-Json

try {
    $resultado = Invoke-RestMethod -Uri "http://localhost:8081/departamentos" `
        -Method Post -ContentType "application/json" -Body $dept
    Write-Host "✅ Departamento creado: $($resultado.id) - $($resultado.nombre)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Crear Empleado
Write-Host "2. Creando empleado Juan Pérez..." -ForegroundColor Yellow
$emp = @{
    id = "E001"
    nombre = "Juan Pérez"
    email = "juan@empresa.com"
    departamentoId = "IT"
} | ConvertTo-Json

try {
    $resultado = Invoke-RestMethod -Uri "http://localhost:8080/empleados" `
        -Method Post -ContentType "application/json" -Body $emp
    Write-Host "✅ Empleado creado: $($resultado.id) - $($resultado.nombre)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Verificar Empleado
Write-Host "3. Verificando empleado existe..." -ForegroundColor Yellow
try {
    $resultado = Invoke-RestMethod -Uri "http://localhost:8080/empleados/E001" -Method Get
    Write-Host "✅ Empleado encontrado: $($resultado.nombre) - $($resultado.email)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Intentar crear empleado con departamento inexistente
Write-Host "4. Intentando crear empleado con departamento inexistente (debe fallar)..." -ForegroundColor Yellow
$empInvalido = @{
    id = "E002"
    nombre = "María García"
    email = "maria@empresa.com"
    departamentoId = "NOEXISTE"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8080/empleados" `
        -Method Post -ContentType "application/json" -Body $empInvalido
    Write-Host "❌ ERROR: Debería haber fallado!" -ForegroundColor Red
} catch {
    Write-Host "✅ Correctamente rechazado: $($_.Exception.Message)" -ForegroundColor Green
}
Write-Host ""

# 5. Listar empleados
Write-Host "5. Listando todos los empleados..." -ForegroundColor Yellow
try {
    $empleados = Invoke-RestMethod -Uri "http://localhost:8080/empleados" -Method Get
    Write-Host "✅ Se encontraron $($empleados.Count) empleado(s)" -ForegroundColor Green
    $empleados | ForEach-Object { Write-Host "   - $($_.id): $($_.nombre)" }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 6. Listar departamentos
Write-Host "6. Listando todos los departamentos..." -ForegroundColor Yellow
try {
    $departamentos = Invoke-RestMethod -Uri "http://localhost:8081/departamentos" -Method Get
    Write-Host "✅ Se encontraron $($departamentos.Count) departamento(s)" -ForegroundColor Green
    $departamentos | ForEach-Object { Write-Host "   - $($_.id): $($_.nombre)" }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "PRUEBA COMPLETADA" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Los datos creados permanecerán en el sistema." -ForegroundColor Yellow
Write-Host "Puedes eliminarlos manualmente o dejar que los tests automatizados los limpien." -ForegroundColor Yellow
```

---

## 📝 Notas

- **Servicios deben estar corriendo**: Asegúrate de haber ejecutado `docker-compose up --build`
- **Puertos**: 
  - Departamentos: `http://localhost:8081`
  - Empleados: `http://localhost:8080`
- **Swagger UI**:
  - Departamentos: http://localhost:8081/docs
  - Empleados: http://localhost:8080/swagger-ui.html
- **IDs únicos**: Si ejecutas los comandos múltiples veces, cambia los IDs para evitar conflictos

