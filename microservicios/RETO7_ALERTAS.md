# 🚨 Guía de Alertas y Notificaciones - Fase 4

## Resumen

La **Fase 4** está completa con:
- ✅ 2 dashboards en Grafana (Health & Performance, Logs & Traces)
- ✅ 4 Alert Rules configuradas
- ✅ Notificaciones Discord integradas

---

## 📊 Alertas Configuradas

### 1. **Service Down** (Crítica 🚨)
- **Condición**: Cualquier servicio retorna `up == 0`
- **Duración**: 2 minutos
- **Severity**: `critical`
- **Mensaje Discord**: "❌ [servicio] está caído!"

### 2. **High Latency** (Advertencia ⚠️)
- **Condición**: P99 latency > 1000ms
- **Duración**: 5 minutos
- **Severity**: `warning`
- **Mensaje Discord**: "⚠️ [servicio] tiene latencia alta"

### 3. **Error Rate Spike** (Advertencia 🔴)
- **Condición**: Tasa de errores 5xx > 5%
- **Duración**: 5 minutos
- **Severity**: `warning`
- **Mensaje Discord**: "🔴 [servicio] tiene tasa de errores alta"

### 4. **Memory Usage** (Advertencia 💾)
- **Condición**: Uso de memoria > 80%
- **Duración**: 5 minutos
- **Severity**: `warning`
- **Mensaje Discord**: "💾 [servicio] está usando mucha memoria"

---

## 🚀 Cómo Ejecutar

### Paso 1: Levantar el Stack

```bash
cd d:\univercidad\micro\ servicios\microservicios

# Construir imágenes
docker-compose build

# Levantar servicios
docker-compose up -d

# Esperar 60 segundos a que Grafana esté listo
Start-Sleep -Seconds 60
```

### Paso 2: Ejecutar el Script de Configuración

```powershell
# Navegar a la carpeta
cd d:\univercidad\micro\ servicios\microservicios

# Ejecutar script de alertas
.\setup-grafana-alerts.ps1

# Si necesitas especificar el webhook personalizado:
.\setup-grafana-alerts.ps1 `
  -GrafanaUrl "http://localhost:3000" `
  -AdminUser "admin" `
  -AdminPassword "admin" `
  -DiscordWebhookUrl "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID"
```

### Paso 3: Verificar la Configuración

```bash
# Ver logs del script
# Si todo está en verde ✅, las alertas están configuradas

# Verificar en Grafana:
# http://localhost:3000
# → Alerting > Alert Rules
# → Debería mostrar 4 reglas activas
```

---

## 📬 Notificaciones Discord

### Cómo Funcionan

```
Prometheus         Grafana            Discord
   ↓                  ↓                   ↓
Métrica violada  → Alert Rule dispara → Webhook POST
(up == 0)           → Formatea mensaje    → Notificación
                     → Envía a Discord      enviada
```

### Formato de Mensaje

Cuando se dispara una alerta, Discord recibe:

```json
{
  "username": "Grafana Alert",
  "avatar_url": "https://grafana.com/favicon.ico",
  "embeds": [{
    "title": "🚨 Service is DOWN",
    "description": "empleados-service is down! Check immediately!",
    "color": 15158332,
    "fields": [
      {
        "name": "Service",
        "value": "empleados-service",
        "inline": true
      },
      {
        "name": "Status",
        "value": "ALERTING",
        "inline": true
      },
      {
        "name": "Severity",
        "value": "critical",
        "inline": false
      }
    ]
  }]
}
```

---

## 🧪 Prueba de Alertas Manualmente

### Test 1: Simular Falla de Servicio

```bash
# Detener Empleados Service
docker-compose stop empleados-service

# En 2-3 minutos, Discord recibirá:
# "🚨 empleados-service is DOWN"

# Reiniciar servicio
docker-compose start empleados-service

# Discord recibirá:
# "✅ empleados-service is back UP"
```

### Test 2: Simular Alta Latencia

Modificar [gestion-empleados/src/main/java/com/microservicios/empleados/controller/](no existe - indicar ruta)

```java
@GetMapping("/api/v1/empleados")
public ResponseEntity<?> getEmpleados() {
    try {
        Thread.sleep(2000);  // 2 segundos de latencia
    } catch (InterruptedException e) {
        // ignore
    }
    return ResponseEntity.ok(empleadoService.getAllEmpleados());
}
```

Luego:
```bash
# Generar tráfico
for i in {1..100}; do
    curl http://localhost:8080/api/v1/empleados
done

# En 5 minutos, Discord recibirá:
# "⚠️ High Request Latency Detected"
```

### Test 3: Simular Alta Tasa de Errores

Modificar un endpoint para retornar 500:

```java
@GetMapping("/api/v1/empleados")
public ResponseEntity<?> getEmpleados() {
    return ResponseEntity.status(500).body("Internal Error");
}
```

Luego:
```bash
# Generar tráfico
for i in {1..100}; do
    curl http://localhost:8080/api/v1/empleados
done

# En 5 minutos, Discord recibirá:
# "🔴 Error Rate Spike: 100%"
```

---

## 🔗 Webhook Discord

Tu webhook ya está configurado en el `.env`:

```
Discord: https://discord.com/api/webhooks/1503990538926428231/apQdq-TJOeg2I06hgQ0js2uRhPp3vq-IqKKBQ81Ukoje-X4X130lhhAIDy8HBtqnt6n0
```

### Para Cambiar el Webhook

Opción 1: Actualizar variable de entorno en `docker-compose.yml`

```yaml
grafana:
  environment:
    DISCORD_WEBHOOK_URL: "https://discord.com/api/webhooks/YOUR_NEW_ID/YOUR_NEW_TOKEN"
```

Opción 2: Pasar como parámetro al script

```powershell
.\setup-grafana-alerts.ps1 -DiscordWebhookUrl "https://discord.com/api/webhooks/..."
```

---

## 📋 Archivos Creados/Modificados

| Archivo | Descripción |
|---------|------------|
| `docker-compose.yml` | Actualizado con DISCORD_WEBHOOK_URL |
| `observability/grafana-notifiers.json` | Configuración de notificadores |
| `observability/alert-rules.yml` | Definición de reglas de alerta |
| `setup-grafana-alerts.ps1` | Script de configuración automática |

---

## 🎯 Verificar Alertas en Grafana

1. Abre http://localhost:3000
2. Navega a **Alerting** → **Alert Rules**
3. Deberías ver:
   - ✅ Service Down
   - ✅ High Latency
   - ✅ Error Rate
   - ✅ Memory Usage

---

## 🔔 Notification Channels

Para ver los channels configurados:

1. http://localhost:3000
2. **Alerting** → **Notification Channels**
3. Deberías ver:
   - ✅ Discord Alert Channel (default)

---

## 🚨 Solución de Problemas

### Las alertas no se disparan

**Problema**: Alert rules existen pero no disparan

**Solución**:
```bash
# 1. Verificar que Prometheus esté scrapeando
curl http://localhost:9090/api/v1/targets

# 2. Verificar que hay datos de métricas
curl "http://localhost:9090/api/v1/query?query=up"

# 3. Ejecutar el script nuevamente
.\setup-grafana-alerts.ps1
```

### Discord no recibe notificaciones

**Problema**: Alertas se disparan pero Discord no recibe nada

**Solución**:
```bash
# 1. Verificar webhook está correcto
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message"}'

# 2. Si recibiste el mensaje, el webhook es válido
# 3. Verificar que Grafana esté conectado a Discord

# En Grafana > Alerting > Contact Points
# Debería mostrar "Discord Alert Channel"
```

### Script dice "Grafana no disponible"

**Problema**: Script falla después de 60 segundos

**Solución**:
```bash
# 1. Verificar que Grafana esté corriendo
docker-compose ps

# 2. Si está corriendo, esperar más tiempo
Start-Sleep -Seconds 120

# 3. Ejecutar el script nuevamente
.\setup-grafana-alerts.ps1
```

---

## 📚 Referencia de Comandos

```bash
# Ver todas las alertas configuradas
curl -u admin:admin http://localhost:3000/api/v1/provisioning/alert-rules

# Ver notification channels
curl -u admin:admin http://localhost:3000/api/v1/provisioning/contact-points

# Test manual de webhook
curl -X POST "DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "content":"🚨 Test Alert from Grafana!",
    "embeds":[{
      "title":"Test Alert",
      "description":"This is a test"
    }]
  }'
```

---

## ✅ Checklist Fase 4

- [x] Discord webhook configurado
- [x] Alert rules definidas (4 tipos)
- [x] Notification channel creado
- [x] Script de automatización creado
- [x] Documentación completa
- [ ] Pruebas de caos ejecutadas (Fase 5)

---

## 🎓 Aprendizaje

**Alert Lifecycle** en Grafana:

```
1. Métrica violada (up == 0)
   ↓
2. Prometheus evalúa each 30s
   ↓
3. Si condición > "for" duration (2m):
   → Estado = ALERTING
   ↓
4. Grafana ve ALERTING → dispatch
   ↓
5. Envía webhook POST a Discord
   ↓
6. Discord notifica al canal
```

---

**Última actualización**: 13 de Mayo de 2026  
**Fase 4**: ✅ Completada  
**Próximo**: Fase 5 - Pruebas de Caos
