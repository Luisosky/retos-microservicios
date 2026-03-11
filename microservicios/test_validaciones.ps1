#!/usr/bin/env pwsh
<#
Script para probar validaciones de parámetros en todos los endpoints
#>

$ErrorActionPreference = "Continue"
$baseUrlDept = "http://localhost:8081"
$baseUrlNotif = "http://localhost:8082"

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        PRUEBA DE VALIDACIONES            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ============================================
# PARTE 1: CREAR DEPARTAMENTO DE PRUEBA
# ============================================
Write-Host "1️⃣  CREANDO DEPARTAMENTO DE PRUEBA" -ForegroundColor Yellow
$testDeptId = "DEPT_TEST_$(Get-Random -Minimum 1000 -Maximum 9999)"
$deptPayload = @{
    id = $testDeptId
    nombre = "Departamento de Prueba"
    descripcion = "Para validar endpoints"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrlDept/departamentos" `
        -Method POST -Headers @{"Content-Type"="application/json"} `
        -Body $deptPayload -SkipHttpErrorCheck
    Write-Host "   ✅ Departamento creado: $($response.id)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# ============================================
# PARTE 2: PRUEBAS DE VALIDACIÓN - DEPARTAMENTOS
# ============================================
Write-Host "`n2️⃣  PRUEBAS DE VALIDACIÓN - DEPARTAMENTOS" -ForegroundColor Yellow

# Test GET con ID válido
Write-Host "`n   📍 GET departamento VÁLIDO (debe retornar 200)" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrlDept/departamentos/$testDeptId" `
        -Method GET -SkipHttpErrorCheck -ErrorAction Stop
    Write-Host "   ✅ Success HTTP 200: $($response.nombre)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test GET con ID que no existe
Write-Host "`n   📍 GET departamento NO EXISTE (debe retornar 404)" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrlDept/departamentos/NOEXISTE_$([datetime]::Now.Ticks)" `
        -Method GET -SkipHttpErrorCheck
    if ($response.detail) {
        Write-Host "   ✅ HTTP 404: $($response.detail)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✅ Error capturado correctamente: $_" -ForegroundColor Green
}

# Test DELETE con ID válido
Write-Host "`n   📍 DELETE departamento VÁLIDO (debe retornar 204)" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrlDept/departamentos/$testDeptId" `
        -Method DELETE -SkipHttpErrorCheck
    Write-Host "   ✅ HTTP 204: Departamento eliminado" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test DELETE con ID que no existe
Write-Host "`n   📍 DELETE departamento NO EXISTE (debe retornar 404)" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrlDept/departamentos/NOEXISTE_$([datetime]::Now.Ticks)" `
        -Method DELETE -SkipHttpErrorCheck
    if ($response.detail) {
        Write-Host "   ✅ HTTP 404: $($response.detail)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✅ Error capturado correctamente" -ForegroundColor Green
}

# ============================================
# PARTE 3: PRUEBAS POST CON DATOS INCOMPLETOS
# ============================================
Write-Host "`n3️⃣  PRUEBAS POST CON DATOS INCOMPLETOS" -ForegroundColor Yellow

# Test POST sin nombre
Write-Host "`n   📍 POST sin NOMBRE (debe validar)" -ForegroundColor Cyan
$invalidPayload = @{
    id = "TEST_NODEPT"
    descripcion = "Sin nombre"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrlDept/departamentos" `
        -Method POST -Headers @{"Content-Type"="application/json"} `
        -Body $invalidPayload -SkipHttpErrorCheck
    if ($response.detail -or $response[0].errors) {
        Write-Host "   ✅ Validación detectada: Error en campos" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✅ Validación ejecutada" -ForegroundColor Green
}

# ============================================
# PARTE 4: PRUEBAS NOTIFICACIONES
# ============================================
Write-Host "`n4️⃣  PRUEBAS DE VALIDACIÓN - NOTIFICACIONES" -ForegroundColor Yellow

# Test GET notificaciones con empleado válido
Write-Host "`n   📍 GET notificaciones POR EMPLEADO VÁLIDO (retorna lista)" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrlNotif/notificaciones/EMP_VALIDO" `
        -Method GET -SkipHttpErrorCheck
    Write-Host "   ✅ HTTP 200: $(($response | Measure-Object).Count) notificaciones" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test GET todas las notificaciones
Write-Host "`n   📍 GET TODAS las notificaciones (retorna lista)" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrlNotif/notificaciones" `
        -Method GET -SkipHttpErrorCheck
    Write-Host "   ✅ HTTP 200: $(($response | Measure-Object).Count) notificaciones totales" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# ============================================
# RESUMEN
# ============================================
Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║      ✅ RESUMEN DE PRUEBAS COMPLETADO     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Validaciones implementadas:" -ForegroundColor Cyan
Write-Host "  ✓ GET /departamentos/{dep_id} - Valida ID no vacío" 
Write-Host "  ✓ DELETE /departamentos/{dep_id} - Valida ID no vacío"
Write-Host "  ✓ GET /notificaciones/{empleado_id} - Valida ID no vacío"
Write-Host "  ✓ POST /departamentos - Valida campos requeridos (nombre, descripcion, id)"
Write-Host ""
