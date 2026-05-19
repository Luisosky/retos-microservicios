# Script para ejecutar los tests del sistema
# Ejecuta los tests de integración end-to-end

Write-Host "================================" -ForegroundColor Cyan
Write-Host "TESTS DEL SISTEMA - Microservicios" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que los servicios estén corriendo
Write-Host "Verificando servicios Docker..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}" | Out-String

if ($containers -notmatch "empleados-service" -or $containers -notmatch "departamentos") {
    Write-Host ""
    Write-Host "ERROR: Los servicios no están corriendo!" -ForegroundColor Red
    Write-Host "Por favor ejecuta primero: docker-compose up --build" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "Servicios encontrados:" -ForegroundColor Green
docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String -Pattern "empleados|departamentos|redis|rabbitmq"
Write-Host ""

# Verificar que Python está instalado
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python no está instalado!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Instalar dependencias si es necesario
if (!(Test-Path "venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Instalando dependencias..." -ForegroundColor Yellow
pip install -q -r requirements.txt

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "EJECUTANDO TESTS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Ejecutar tests
python -m pytest test_system_integration.py -v -s --tb=short

$testResult = $LASTEXITCODE

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
if ($testResult -eq 0) {
    Write-Host "TESTS COMPLETADOS EXITOSAMENTE" -ForegroundColor Green
} else {
    Write-Host "ALGUNOS TESTS FALLARON" -ForegroundColor Red
}
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

exit $testResult

