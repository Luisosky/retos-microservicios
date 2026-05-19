# Quick Start - Reto 7: Observabilidad Completa
# ============================================
# Este script levanta el stack completo de observabilidad
# con dashboards y alertas configuradas

Write-Host "🚀 Iniciando Reto 7 - Observabilidad y Monitoreo..." -ForegroundColor Cyan

# Variables
$DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1503990538926428231/apQdq-TJOeg2I06hgQ0js2uRhPp3vq-IqKKBQ81Ukoje-X4X130lhhAIDy8HBtqnt6n0"
$GRAFANA_URL = "http://localhost:3000"
$PROMETHEUS_URL = "http://localhost:9090"
$ZIPKIN_URL = "http://localhost:9411"
$LOKI_URL = "http://localhost:3100"

Write-Host "`n📁 Navegar a carpeta del proyecto..." -ForegroundColor Yellow
Set-Location "d:\univercidad\micro servicios\microservicios"

Write-Host "✅ Carpeta actual: $(Get-Location)" -ForegroundColor Green

# ============================================
# Step 1: Build & Up
# ============================================
Write-Host "`n🔨 Construyendo imágenes Docker..." -ForegroundColor Cyan
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en docker-compose build" -ForegroundColor Red
    exit 1
}

Write-Host "`n🐳 Levantando servicios..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en docker-compose up" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Servicios levantados" -ForegroundColor Green

# ============================================
# Step 2: Esperar a que Grafana esté listo
# ============================================
Write-Host "`n⏳ Esperando a que Grafana esté listo (máximo 120 segundos)..." -ForegroundColor Yellow

$maxRetries = 60
$retryCount = 0
$grafanaReady = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "$GRAFANA_URL/api/health" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $grafanaReady = $true
            Write-Host "✅ Grafana está listo!" -ForegroundColor Green
            break
        }
    } catch {
        $retryCount++
        Write-Host "  Intento $retryCount/$maxRetries..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $grafanaReady) {
    Write-Host "⚠️  Grafana aún está iniciando, continuando con la configuración..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# ============================================
# Step 3: Mostrar estado de servicios
# ============================================
Write-Host "`n📊 Estado de servicios Docker:" -ForegroundColor Cyan
docker-compose ps

# ============================================
# Step 4: Mostrar URLs de acceso
# ============================================
Write-Host "`n🌐 URLs de Acceso:" -ForegroundColor Green
Write-Host "   📊 Grafana (Dashboards)        → $GRAFANA_URL" -ForegroundColor Cyan
Write-Host "   📈 Prometheus (Métricas)      → $PROMETHEUS_URL" -ForegroundColor Cyan
Write-Host "   🔀 Zipkin (Trazas)            → $ZIPKIN_URL" -ForegroundColor Cyan
Write-Host "   📝 Loki (Logs)                → $LOKI_URL" -ForegroundColor Cyan

Write-Host "`n📋 Credenciales Grafana:" -ForegroundColor Green
Write-Host "   👤 Usuario: admin" -ForegroundColor Cyan
Write-Host "   🔑 Contraseña: admin" -ForegroundColor Cyan

# ============================================
# Step 5: Ejecutar script de alertas
# ============================================
Write-Host "`n🔧 Configurando Alertas y Notificaciones Discord..." -ForegroundColor Cyan

if (Test-Path ".\setup-grafana-alerts.ps1") {
    Write-Host "   ▶️  Ejecutando setup-grafana-alerts.ps1..." -ForegroundColor Yellow
    & .\setup-grafana-alerts.ps1 `
        -GrafanaUrl $GRAFANA_URL `
        -AdminUser "admin" `
        -AdminPassword "admin" `
        -DiscordWebhookUrl $DISCORD_WEBHOOK
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Alertas configuradas exitosamente" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Algunos warnings en la configuración de alertas" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Script setup-grafana-alerts.ps1 no encontrado" -ForegroundColor Yellow
}

# ============================================
# Step 6: Información de dashboards
# ============================================
Write-Host "`n📊 Dashboards Disponibles:" -ForegroundColor Green
Write-Host "   1. Microservices Health & Performance" -ForegroundColor Cyan
Write-Host "      → Estado de servicios, requests, latencia, errores" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan
Write-Host "   2. Logs & Traces Explorer" -ForegroundColor Cyan
Write-Host "      → Volumen de logs, nivel de severidad, error logs" -ForegroundColor Gray

# ============================================
# Step 7: Alertas activas
# ============================================
Write-Host "`n🚨 Alertas Configuradas:" -ForegroundColor Green
Write-Host "   1. 🚨 Service Down (crítica)" -ForegroundColor Red
Write-Host "      → Si cualquier servicio retorna up=0 por 2 minutos" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan
Write-Host "   2. ⚠️  High Latency (warning)" -ForegroundColor Yellow
Write-Host "      → Si P99 latency > 1000ms por 5 minutos" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan
Write-Host "   3. 🔴 Error Rate Spike (warning)" -ForegroundColor Yellow
Write-Host "      → Si tasa de errores 5xx > 5% por 5 minutos" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan
Write-Host "   4. 💾 Memory Usage High (warning)" -ForegroundColor Yellow
Write-Host "      → Si uso de memoria > 80% por 5 minutos" -ForegroundColor Gray

# ============================================
# Step 8: Próximos pasos
# ============================================
Write-Host "`n📋 Próximos Pasos (Fase 5 - Pruebas):" -ForegroundColor Green
Write-Host "" -ForegroundColor Cyan
Write-Host "   1️⃣  Generar tráfico:" -ForegroundColor Yellow
Write-Host "      `$env:EMPLOYEES_API='http://localhost:8080'" -ForegroundColor Gray
Write-Host "      for (`$i=0; `$i -lt 100; `$i++) {" -ForegroundColor Gray
Write-Host "          curl -X POST `$env:EMPLOYEES_API/api/v1/empleados " + `
            "-H 'Content-Type: application/json' " + `
            "-d '{`"nombre`":`"Test`",`"apellido`":`"User`"}'" -ForegroundColor Gray
Write-Host "      }" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan
Write-Host "   2️⃣  Simular falla de servicio:" -ForegroundColor Yellow
Write-Host "      docker-compose stop empleados-service" -ForegroundColor Gray
Write-Host "      # Esperar 2-3 minutos para ver alerta en Discord" -ForegroundColor Gray
Write-Host "      docker-compose start empleados-service" -ForegroundColor Gray
Write-Host "" -ForegroundColor Cyan
Write-Host "   3️⃣  Inducir latencia:" -ForegroundColor Yellow
Write-Host "      # Modificar controller de empleados con Thread.sleep(2000)" -ForegroundColor Gray
Write-Host "      # Generar tráfico nuevamente" -ForegroundColor Gray
Write-Host "      # Ver latencia en dashboard después de 5 minutos" -ForegroundColor Gray

# ============================================
# Step 9: Verificación final
# ============================================
Write-Host "`n✅ Verificación Rápida:" -ForegroundColor Green
Write-Host "   • Docker Compose: $(docker-compose ps -q | Measure-Object -Line).Lines servicios corriendo" -ForegroundColor Cyan
Write-Host "   • Grafana: Abierto en $GRAFANA_URL" -ForegroundColor Cyan
Write-Host "   • Prometheus: Abierto en $PROMETHEUS_URL/targets" -ForegroundColor Cyan
Write-Host "   • Discord: Conectado a webhook" -ForegroundColor Cyan

# ============================================
# Finalización
# ============================================
Write-Host "`n✨ Setup Completado!" -ForegroundColor Green
Write-Host "`n📖 Documentación:" -ForegroundColor Cyan
Write-Host "   • OBSERVABILITY.md          → Conceptos teóricos" -ForegroundColor Gray
Write-Host "   • RETO7_EJECUCION.md        → Guía de ejecución" -ForegroundColor Gray
Write-Host "   • RETO7_ALERTAS.md          → Configuración de alertas" -ForegroundColor Gray
Write-Host "   • INDEX_RETO7.md            → Índice completo" -ForegroundColor Gray
Write-Host "   • observability/README.md   → Detalles técnicos" -ForegroundColor Gray

Write-Host "`n🎯 Fase 4 Completada: Visualización y Alertas ✅" -ForegroundColor Green
Write-Host "🔄 Próximo: Fase 5 - Pruebas de Caos" -ForegroundColor Yellow
Write-Host "`n"
