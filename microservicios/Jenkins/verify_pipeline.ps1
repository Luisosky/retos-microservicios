# Script de verificación para Pipeline CI de Empleados (Reto 6 - Parte 2)
# Valida que Jenkins, credenciales y el Jenkinsfile estén correctamente configurados
# Versión: PowerShell (Windows)

param(
    [switch]$Verbose = $false
)

function Write-Status {
    param(
        [string]$Message,
        [ValidateSet("Success", "Error", "Warning", "Info")]
        [string]$Status = "Info"
    )
    
    $colors = @{
        "Success" = [ConsoleColor]::Green
        "Error"   = [ConsoleColor]::Red
        "Warning" = [ConsoleColor]::Yellow
        "Info"    = [ConsoleColor]::Cyan
    }
    
    $symbols = @{
        "Success" = "✓"
        "Error"   = "✗"
        "Warning" = "⚠"
        "Info"    = "ℹ"
    }
    
    $color = $colors[$Status]
    $symbol = $symbols[$Status]
    
    Write-Host "$symbol $Message" -ForegroundColor $color
}

Write-Host "=================================================="
Write-Host "Verificación del Pipeline CI - Reto 6 Parte 2" -ForegroundColor Cyan
Write-Host "=================================================="
Write-Host ""

# 1. Verificar que Jenkins está ejecutándose
Write-Host "1️⃣  Verificando servicio Jenkins..." -ForegroundColor Cyan
try {
    $containers = docker ps --filter "name=jenkins-server" --quiet
    if ($containers) {
        Write-Status "Jenkins container está ejecutándose" "Success"
    }
    else {
        Write-Status "Jenkins no está ejecutándose" "Error"
        Write-Host "  Ejecuta: docker-compose up -d jenkins"
        exit 1
    }
}
catch {
    Write-Status "Error verificando Docker: $_" "Error"
    exit 1
}

# 2. Verificar conectividad a Jenkins
Write-Host ""
Write-Host "2️⃣  Verificando conectividad a Jenkins (puerto 9090)..." -ForegroundColor Cyan
$attempts = 0
$max_attempts = 5
while ($attempts -lt $max_attempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9090/login" -Method Head -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Status "Jenkins responde en http://localhost:9090" "Success"
            break
        }
    }
    catch {
        $attempts++
        if ($attempts -lt $max_attempts) {
            Write-Status "Jenkins aún está iniciando, esperando... ($attempts/$max_attempts)" "Warning"
            Start-Sleep -Seconds 5
        }
    }
}

if ($attempts -eq $max_attempts) {
    Write-Status "No se pudo conectar a Jenkins después de 25 segundos" "Warning"
}

# 3. Verificar que Jenkinsfile existe
Write-Host ""
Write-Host "3️⃣  Verificando archivos necesarios..." -ForegroundColor Cyan

if (Test-Path "gestion-empleados/Jenkinsfile") {
    Write-Status "Jenkinsfile existe" "Success"
}
else {
    Write-Status "Jenkinsfile no encontrado" "Error"
    exit 1
}

if (Test-Path "gestion-empleados/pom.xml") {
    Write-Status "pom.xml existe" "Success"
}
else {
    Write-Status "pom.xml no encontrado" "Error"
    exit 1
}

# 4. Verificar casc.yaml tiene credenciales
Write-Host ""
Write-Host "4️⃣  Verificando configuración JCasC..." -ForegroundColor Cyan

$cascContent = Get-Content "Jenkins/casc.yaml" -Raw
if ($cascContent -match "jwt-secret-key") {
    Write-Status "Credencial JWT definida en casc.yaml" "Success"
}
else {
    Write-Status "Credencial JWT no encontrada en casc.yaml" "Error"
    exit 1
}

if ($cascContent -match "Empleados-Pipeline") {
    Write-Status "Job DSL 'Empleados-Pipeline' definido" "Success"
}
else {
    Write-Status "Job DSL 'Empleados-Pipeline' no encontrado" "Warning"
}

# 5. Verificar Docker socket (simulado en Windows)
Write-Host ""
Write-Host "5️⃣  Verificando Docker Socket Mount..." -ForegroundColor Cyan
try {
    docker exec jenkins-server test -e /var/run/docker.sock | Out-Null
    Write-Status "Docker socket accesible desde Jenkins" "Success"
}
catch {
    Write-Status "Docker socket no accesible (puede ser esperado en Windows)" "Warning"
}

# 6. Verificar Docker CLI en Jenkins
Write-Host ""
Write-Host "6️⃣  Verificando Docker CLI en Jenkins..." -ForegroundColor Cyan
try {
    $dockerVersion = docker exec jenkins-server docker --version 2>$null
    if ($dockerVersion) {
        Write-Status "Docker CLI disponible: $dockerVersion" "Success"
    }
    else {
        Write-Status "Docker CLI no disponible" "Error"
    }
}
catch {
    Write-Status "Error verificando Docker CLI: $_" "Warning"
}

# 7. Verificar Maven image
Write-Host ""
Write-Host "7️⃣  Verificando Maven..." -ForegroundColor Cyan
Write-Status "Maven image será descargada en primer build" "Info"

# 8. Verificar Plugins
Write-Host ""
Write-Host "8️⃣  Verificando plugins instalados..." -ForegroundColor Cyan
try {
    $plugins = docker exec jenkins-server ls /var/jenkins_home/plugins/ 2>$null
    if ($plugins -match "configuration-as-code") {
        Write-Status "Plugin 'configuration-as-code' instalado" "Success"
    }
    if ($plugins -match "workflow-aggregator") {
        Write-Status "Plugin 'workflow-aggregator' instalado" "Success"
    }
    if ($plugins -match "docker-pipeline") {
        Write-Status "Plugin 'docker-pipeline' instalado" "Success"
    }
}
catch {
    Write-Status "Esperando a que se instalen los plugins..." "Warning"
}

# 9. Verificar variables de entorno
Write-Host ""
Write-Host "🔟 Verificando variables de entorno..." -ForegroundColor Cyan
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "^JWT_SECRET=(.+)$") {
        $jwtValue = ($envContent | Select-String "^JWT_SECRET=(.+)$").Matches[0].Groups[1].Value
        if ($jwtValue.Length -ge 32) {
            Write-Status "JWT_SECRET configurada ($($jwtValue.Length) caracteres)" "Success"
        }
        else {
            Write-Status "JWT_SECRET muy corta (mínimo 32 caracteres)" "Error"
        }
    }
    else {
        Write-Status "JWT_SECRET no configurada en .env" "Warning"
    }
}
else {
    Write-Status "Archivo .env no encontrado (usando valores por defecto)" "Warning"
}

# Resumen final
Write-Host ""
Write-Host "=================================================="
Write-Host "✅ Verificación completada" -ForegroundColor Green
Write-Host "=================================================="
Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acceder a Jenkins:"
Write-Host "   http://localhost:9090" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Ejecutar el pipeline:"
Write-Host "   - Ir a 'Empleados-Pipeline'" -ForegroundColor Yellow
Write-Host "   - Click en 'Build Now'" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Ver logs en tiempo real:"
Write-Host "   docker logs jenkins-server -f" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Ver reportes:"
Write-Host "   - JaCoCo: Jenkins UI → Empleados-Pipeline → Build → JaCoCo Coverage Report" -ForegroundColor Yellow
Write-Host "   - Tests: Jenkins UI → Empleados-Pipeline → Build → Test Report" -ForegroundColor Yellow
Write-Host ""
