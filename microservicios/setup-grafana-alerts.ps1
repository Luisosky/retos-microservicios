# Script de Configuración de Alertas en Grafana
# ==============================================
# Este script configura el notification channel de Discord
# y las alert rules en Grafana automáticamente

param(
    [string]$GrafanaUrl = "http://localhost:3000",
    [string]$AdminUser = "admin",
    [string]$AdminPassword = "admin",
    [string]$DiscordWebhookUrl = "https://discord.com/api/webhooks/1503990538926428231/apQdq-TJOeg2I06hgQ0js2uRhPp3vq-IqKKBQ81Ukoje-X4X130lhhAIDy8HBtqnt6n0"
)

# Función auxiliar para hacer requests a Grafana API
function Invoke-GrafanaAPI {
    param(
        [string]$Method,
        [string]$Path,
        [object]$Body
    )
    
    $headers = @{
        "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($AdminUser):$($AdminPassword)"))
        "Content-Type" = "application/json"
    }
    
    $url = "$GrafanaUrl/api$Path"
    
    try {
        if ($Body) {
            $response = Invoke-WebRequest -Method $Method -Uri $url -Headers $headers -Body ($Body | ConvertTo-Json -Depth 10) -UseBasicParsing
        } else {
            $response = Invoke-WebRequest -Method $Method -Uri $url -Headers $headers -UseBasicParsing
        }
        return $response.Content | ConvertFrom-Json
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

Write-Host "🔧 Configurando Grafana para Observabilidad..." -ForegroundColor Cyan

# 1. Esperar a que Grafana esté disponible
Write-Host "⏳ Esperando a que Grafana esté disponible..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
$grafanaReady = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "$GrafanaUrl/api/health" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $grafanaReady = $true
            Write-Host "✅ Grafana está listo" -ForegroundColor Green
            break
        }
    } catch {
        $retryCount++
        Write-Host "  Intento $retryCount/$maxRetries..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $grafanaReady) {
    Write-Host "❌ Grafana no está disponible después de 60 segundos" -ForegroundColor Red
    exit 1
}

# 2. Crear Notification Channel de Discord
Write-Host "`n📨 Creando Notification Channel de Discord..." -ForegroundColor Cyan

$notificationChannelBody = @{
    "name" = "Discord Alert Channel"
    "type" = "discord"
    "isDefault" = $true
    "sendReminder" = $true
    "frequency" = "15m"
    "settings" = @{
        "url" = $DiscordWebhookUrl
    }
}

$notificationResponse = Invoke-GrafanaAPI -Method "POST" -Path "/v1/provisioning/contact-points" -Body $notificationChannelBody

if ($notificationResponse -and $notificationResponse.id) {
    Write-Host "✅ Notification Channel creado: $($notificationResponse.name)" -ForegroundColor Green
} else {
    Write-Host "⚠️  No se pudo crear el channel (puede ya existir)" -ForegroundColor Yellow
}

# 3. Crear Alert Rule 1: Service Down
Write-Host "`n🚨 Creando Alert Rule: Service Down..." -ForegroundColor Cyan

$alertRule1 = @{
    "uid" = "service-down-alert-001"
    "title" = "🚨 Service is DOWN"
    "condition" = "A"
    "data" = @(
        @{
            "refId" = "A"
            "queryType" = ""
            "relativeTimeRange" = @{
                "from" = 600
                "to" = 0
            }
            "datasourceUid" = "prometheus"
            "model" = @{
                "expr" = 'up{job=~".*-service"} == 0'
                "interval" = ""
                "legendFormat" = ""
                "refId" = "A"
            }
        }
    )
    "noDataState" = "NoData"
    "execErrState" = "Alerting"
    "for" = "2m"
    "annotations" = @{
        "description" = "{{ \$labels.job }} is down! Immediate action required."
        "summary" = "Service {{ \$labels.job }} is not responding"
    }
    "labels" = @{
        "severity" = "critical"
        "team" = "platform"
    }
}

$alertResponse1 = Invoke-GrafanaAPI -Method "POST" -Path "/v1/provisioning/alert-rules" -Body $alertRule1

if ($alertResponse1 -and $alertResponse1.uid) {
    Write-Host "✅ Alert Rule creada: Service Down" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error creating alert (puede ya existir): $($alertResponse1)" -ForegroundColor Yellow
}

# 4. Crear Alert Rule 2: High Latency
Write-Host "`n⚠️  Creando Alert Rule: High Latency..." -ForegroundColor Cyan

$alertRule2 = @{
    "uid" = "high-latency-alert-002"
    "title" = "⚠️ High Request Latency Detected"
    "condition" = "A"
    "data" = @(
        @{
            "refId" = "A"
            "queryType" = ""
            "relativeTimeRange" = @{
                "from" = 300
                "to" = 0
            }
            "datasourceUid" = "prometheus"
            "model" = @{
                "expr" = 'histogram_quantile(0.99, rate(http_server_requests_seconds_bucket[5m])) > 1'
                "interval" = ""
                "legendFormat" = ""
                "refId" = "A"
            }
        }
    )
    "noDataState" = "NoData"
    "execErrState" = "Alerting"
    "for" = "5m"
    "annotations" = @{
        "description" = "P99 latency for {{ \$labels.service }} is {{ humanizeDuration \$value }}"
        "summary" = "High latency detected on {{ \$labels.service }}"
    }
    "labels" = @{
        "severity" = "warning"
        "team" = "platform"
    }
}

$alertResponse2 = Invoke-GrafanaAPI -Method "POST" -Path "/v1/provisioning/alert-rules" -Body $alertRule2

if ($alertResponse2 -and $alertResponse2.uid) {
    Write-Host "✅ Alert Rule creada: High Latency" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error creating alert (puede ya existir): $($alertResponse2)" -ForegroundColor Yellow
}

# 5. Crear Alert Rule 3: Error Rate
Write-Host "`n🔴 Creando Alert Rule: Error Rate..." -ForegroundColor Cyan

$alertRule3 = @{
    "uid" = "error-rate-alert-003"
    "title" = "🔴 Error Rate Spike"
    "condition" = "A"
    "data" = @(
        @{
            "refId" = "A"
            "queryType" = ""
            "relativeTimeRange" = @{
                "from" = 300
                "to" = 0
            }
            "datasourceUid" = "prometheus"
            "model" = @{
                "expr" = '100 * (rate(http_server_requests_seconds_count{status=~"5.."}[5m]) / ignoring(status) group_left sum by (service) (rate(http_server_requests_seconds_count[5m]))) > 5'
                "interval" = ""
                "legendFormat" = ""
                "refId" = "A"
            }
        }
    )
    "noDataState" = "NoData"
    "execErrState" = "Alerting"
    "for" = "5m"
    "annotations" = @{
        "description" = "Error rate for {{ \$labels.service }} is {{ humanize \$value }}%"
        "summary" = "High error rate detected on {{ \$labels.service }}"
    }
    "labels" = @{
        "severity" = "warning"
        "team" = "platform"
    }
}

$alertResponse3 = Invoke-GrafanaAPI -Method "POST" -Path "/v1/provisioning/alert-rules" -Body $alertRule3

if ($alertResponse3 -and $alertResponse3.uid) {
    Write-Host "✅ Alert Rule creada: Error Rate" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error creating alert (puede ya existir): $($alertResponse3)" -ForegroundColor Yellow
}

# 6. Crear Alert Rule 4: Memory Usage
Write-Host "`n💾 Creando Alert Rule: Memory Usage..." -ForegroundColor Cyan

$alertRule4 = @{
    "uid" = "memory-usage-alert-004"
    "title" = "💾 High Memory Usage"
    "condition" = "A"
    "data" = @(
        @{
            "refId" = "A"
            "queryType" = ""
            "relativeTimeRange" = @{
                "from" = 300
                "to" = 0
            }
            "datasourceUid" = "prometheus"
            "model" = @{
                "expr" = '(process_resident_memory_bytes / 1073741824) > 0.8'
                "interval" = ""
                "legendFormat" = ""
                "refId" = "A"
            }
        }
    )
    "noDataState" = "NoData"
    "execErrState" = "Alerting"
    "for" = "5m"
    "annotations" = @{
        "description" = "Memory usage for {{ \$labels.service }} is high"
        "summary" = "Service {{ \$labels.service }} is using > 80% of allocated memory"
    }
    "labels" = @{
        "severity" = "warning"
        "team" = "platform"
    }
}

$alertResponse4 = Invoke-GrafanaAPI -Method "POST" -Path "/v1/provisioning/alert-rules" -Body $alertRule4

if ($alertResponse4 -and $alertResponse4.uid) {
    Write-Host "✅ Alert Rule creada: Memory Usage" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error creating alert (puede ya existir): $($alertResponse4)" -ForegroundColor Yellow
}

Write-Host "`n✨ Configuración de Grafana completada!" -ForegroundColor Green
Write-Host "`n📊 Acceder a Grafana: $GrafanaUrl" -ForegroundColor Cyan
Write-Host "🔔 Notificaciones: Discord Webhook configurado" -ForegroundColor Cyan
Write-Host "🚨 Alertas activas: Service Down, High Latency, Error Rate, Memory Usage" -ForegroundColor Cyan
