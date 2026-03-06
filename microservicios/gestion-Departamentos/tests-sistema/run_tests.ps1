# Script para ejecutar pruebas del sistema de microservicios
# Flujo de prueba completo del sistema

param(
    [switch]$Build,
    [switch]$SkipCleanup,
    [string]$DepartamentosUrl = "http://localhost:8081",
    [string]$EmpleadosUrl = "http://localhost:8080"
)

# Colores para la consola
function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor Blue
    Write-Host $Message.PadLeft(($Message.Length + 70) / 2) -ForegroundColor Blue
    Write-Host "=" * 70 -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ $Message" -ForegroundColor Cyan
}

function Write-Test {
    param([string]$Message)
    Write-Host "[TEST] $Message..." -ForegroundColor Yellow
}

# Función para esperar que un servicio esté disponible
function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )
    
    Write-Test "Esperando servicio $ServiceName"
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "Servicio $ServiceName disponible"
                return $true
            }
        }
        catch {
            if ($i -lt $MaxAttempts) {
                Write-Info "Intento $i/$MaxAttempts, esperando ${DelaySeconds}s..."
                Start-Sleep -Seconds $DelaySeconds
            }
        }
    }
    
    Write-Error-Message "Servicio $ServiceName no disponible después de $MaxAttempts intentos"
    return $false
}

# Función para hacer peticiones HTTP con manejo de errores
function Invoke-ApiRequest {
    param(
        [string]$Method,
        [string]$Url,
        [object]$Body = $null
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            ContentType = "application/json"
            TimeoutSec = 10
            UseBasicParsing = $true
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Data = ($response.Content | ConvertFrom-Json)
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.Value__
        $errorBody = $null
        
        try {
            $errorBody = $_.ErrorDetails.Message | ConvertFrom-Json
        }
        catch {
            $errorBody = $_.ErrorDetails.Message
        }
        
        return @{
            Success = $false
            StatusCode = $statusCode
            Data = $errorBody
            Error = $_.Exception.Message
        }
    }
}

# INICIO DEL SCRIPT
Write-Header "PRUEBAS DEL SISTEMA - MICROSERVICIOS"

# Paso 1: Iniciar servicios si se solicita
if ($Build) {
    Write-Header "INICIANDO SERVICIOS CON DOCKER COMPOSE"
    Write-Info "Ejecutando: docker-compose up --build -d"
    
    Push-Location -Path (Join-Path $PSScriptRoot "..\..\..")
    docker-compose up --build -d
    $exitCode = $LASTEXITCODE
    Pop-Location
    
    if ($exitCode -ne 0) {
        Write-Error-Message "Error al iniciar los servicios"
        exit 1
    }
    
    Write-Success "Servicios iniciados"
    Write-Info "Esperando 10 segundos para que los servicios se estabilicen..."
    Start-Sleep -Seconds 10
}

# Paso 2: Verificar disponibilidad de servicios
Write-Header "VERIFICANDO DISPONIBILIDAD DE SERVICIOS"

$departamentosAvailable = Wait-ForService -ServiceName "Departamentos" -Url "$DepartamentosUrl/docs"
$empleadosAvailable = Wait-ForService -ServiceName "Empleados" -Url "$EmpleadosUrl/docs"

if (-not $departamentosAvailable -or -not $empleadosAvailable) {
    Write-Error-Message "Los servicios no están disponibles. Ejecute 'docker-compose up' primero."
    exit 1
}

# Paso 3: Ejecutar pruebas
Write-Header "EJECUTANDO PRUEBAS DE INTEGRACIÓN"

$testResults = @()

# Test 1: Crear departamento
Write-Test "1. Crear departamento 'IT'"
$departamentoData = @{
    id = "IT"
    nombre = "Tecnología"
    descripcion = "Departamento de TI"
}

$result = Invoke-ApiRequest -Method POST -Url "$DepartamentosUrl/departamentos" -Body $departamentoData

if ($result.Success -and ($result.StatusCode -eq 200 -or $result.StatusCode -eq 201)) {
    Write-Success "Departamento creado exitosamente (Status: $($result.StatusCode))"
    Write-Info "Respuesta: $($result.Data | ConvertTo-Json -Compress)"
    $testResults += @{ Test = "Crear departamento"; Passed = $true }
} else {
    Write-Error-Message "Error al crear departamento (Status: $($result.StatusCode))"
    Write-Info "Error: $($result.Data)"
    $testResults += @{ Test = "Crear departamento"; Passed = $false }
}

Write-Host ""

# Test 2: Crear empleado válido
Write-Test "2. Crear empleado 'E001' con departamento 'IT'"
$empleadoData = @{
    id = "E001"
    nombre = "Juan Pérez"
    email = "juan@empresa.com"
    departamentoId = "IT"
}

$result = Invoke-ApiRequest -Method POST -Url "$EmpleadosUrl/empleados" -Body $empleadoData

if ($result.Success -and ($result.StatusCode -eq 200 -or $result.StatusCode -eq 201)) {
    Write-Success "Empleado creado exitosamente (Status: $($result.StatusCode))"
    Write-Info "Respuesta: $($result.Data | ConvertTo-Json -Compress)"
    $testResults += @{ Test = "Crear empleado válido"; Passed = $true }
} else {
    Write-Error-Message "Error al crear empleado (Status: $($result.StatusCode))"
    Write-Info "Error: $($result.Data)"
    $testResults += @{ Test = "Crear empleado válido"; Passed = $false }
}

Write-Host ""

# Test 3: Verificar que el empleado existe
Write-Test "3. Verificar empleado 'E001'"
$result = Invoke-ApiRequest -Method GET -Url "$EmpleadosUrl/empleados/E001"

if ($result.Success -and $result.StatusCode -eq 200) {
    Write-Success "Empleado encontrado: $($result.Data.nombre)"
    Write-Info "Email: $($result.Data.email)"
    Write-Info "Departamento: $($result.Data.departamentoId)"
    $testResults += @{ Test = "Verificar empleado existe"; Passed = $true }
} else {
    Write-Error-Message "Empleado no encontrado (Status: $($result.StatusCode))"
    $testResults += @{ Test = "Verificar empleado existe"; Passed = $false }
}

Write-Host ""

# Test 4: Intentar crear empleado con departamento inexistente
Write-Test "4. Intentar crear empleado con departamento inexistente (debe fallar)"
$empleadoInvalidoData = @{
    id = "E002"
    nombre = "María López"
    email = "maria@empresa.com"
    departamentoId = "DEPT_NO_EXISTE"
}

$result = Invoke-ApiRequest -Method POST -Url "$EmpleadosUrl/empleados" -Body $empleadoInvalidoData

if (-not $result.Success -and $result.StatusCode -eq 400) {
    Write-Success "Validación correcta: rechazado con status 400"
    Write-Info "Mensaje: $($result.Data.message)"
    $testResults += @{ Test = "Rechazar departamento inválido"; Passed = $true }
} else {
    Write-Error-Message "Error: se esperaba status 400, obtuvo $($result.StatusCode)"
    $testResults += @{ Test = "Rechazar departamento inválido"; Passed = $false }
}

Write-Host ""

# Test 5: Listar departamentos
Write-Test "5. Listar todos los departamentos"
$result = Invoke-ApiRequest -Method GET -Url "$DepartamentosUrl/departamentos"

if ($result.Success -and $result.StatusCode -eq 200) {
    $count = $result.Data.Count
    Write-Success "Encontrados $count departamento(s)"
    foreach ($dept in $result.Data) {
        Write-Info "  - $($dept.id): $($dept.nombre)"
    }
    $testResults += @{ Test = "Listar departamentos"; Passed = $true }
} else {
    Write-Error-Message "Error al listar departamentos (Status: $($result.StatusCode))"
    $testResults += @{ Test = "Listar departamentos"; Passed = $false }
}

Write-Host ""

# Test 6: Listar empleados
Write-Test "6. Listar todos los empleados"
$result = Invoke-ApiRequest -Method GET -Url "$EmpleadosUrl/empleados"

if ($result.Success -and $result.StatusCode -eq 200) {
    $count = $result.Data.Count
    Write-Success "Encontrados $count empleado(s)"
    foreach ($emp in $result.Data) {
        Write-Info "  - $($emp.id): $($emp.nombre) ($($emp.departamentoId))"
    }
    $testResults += @{ Test = "Listar empleados"; Passed = $true }
} else {
    Write-Error-Message "Error al listar empleados (Status: $($result.StatusCode))"
    $testResults += @{ Test = "Listar empleados"; Passed = $false }
}

Write-Host ""

# Limpieza de datos (opcional)
if (-not $SkipCleanup) {
    Write-Header "LIMPIEZA DE DATOS DE PRUEBA"
    
    Write-Test "Eliminar empleado E001"
    $result = Invoke-ApiRequest -Method DELETE -Url "$EmpleadosUrl/empleados/E001"
    if ($result.Success -or $result.StatusCode -eq 404) {
        Write-Success "Empleado eliminado o no existente"
    }
    
    Write-Test "Eliminar departamento IT"
    $result = Invoke-ApiRequest -Method DELETE -Url "$DepartamentosUrl/departamentos/IT"
    if ($result.Success -or $result.StatusCode -eq 404) {
        Write-Success "Departamento eliminado o no existente"
    }
}

# Resumen de resultados
Write-Header "RESUMEN DE PRUEBAS"

$passed = ($testResults | Where-Object { $_.Passed -eq $true }).Count
$failed = ($testResults | Where-Object { $_.Passed -eq $false }).Count
$total = $testResults.Count

Write-Host "Total de pruebas: $total"
Write-Host "Exitosas: $passed" -ForegroundColor Green
Write-Host "Fallidas: $failed" -ForegroundColor Red

if ($failed -gt 0) {
    Write-Host ""
    Write-Host "Pruebas fallidas:" -ForegroundColor Red
    foreach ($test in ($testResults | Where-Object { $_.Passed -eq $false })) {
        Write-Host "  ✗ $($test.Test)" -ForegroundColor Red
    }
}

$successRate = if ($total -gt 0) { ($passed / $total) * 100 } else { 0 }
Write-Host ""
Write-Host "Tasa de éxito: $([math]::Round($successRate, 1))%"

# Exit code
if ($failed -gt 0) {
    exit 1
} else {
    exit 0
}
