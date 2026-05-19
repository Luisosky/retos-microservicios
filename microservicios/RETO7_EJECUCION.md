# 🚀 Guía de Ejecución - Reto 7 Observabilidad y Monitoreo

## 📋 Resumen de Implementación

Hemos completado las siguientes fases:

### ✅ Fase 1: Diseño y Preparación (Completada)
- [x] Diagrama de arquitectura de observabilidad
- [x] Documentación de conceptos: Métricas, Logs, Trazas
- [x] Explicación Pull vs Push
- [x] Introducción a OpenTelemetry
- [x] Justificación de tecnologías elegidas

### ✅ Fase 2: Stack de Observabilidad Desplegado (Completada)
- [x] Prometheus configurado (puerto 9090)
- [x] Grafana configurado (puerto 3000)
- [x] Zipkin para trazas distribuidas (puerto 9411)
- [x] Loki para agregación de logs (puerto 3100)
- [x] Promtail para recolección de logs
- [x] Red Docker compartida configurada

### 🔄 Fase 3: Instrumentación de Microservicios (80% completada)
- [x] Empleados (Java): Actuator + Micrometer + OpenTelemetry
- [x] Departamentos (Python): Prometheus + OpenTelemetry
- [x] Notificaciones (Python): Dependencias agregadas
- [ ] Autenticación (C#): Pendiente
- [ ] Perfiles (PHP): Pendiente

### ✅ Fase 4: Visualización (Parcialmente completada)
- [x] Dashboard "Microservices Health & Performance" creado
- [x] Dashboard "Logs & Traces Explorer" creado
- [x] Datasources configurados (Prometheus, Loki, Zipkin)
- [ ] Alertas configuradas (pendiente)
- [ ] Notificaciones Discord/Slack (pendiente)

---

## 🎯 Próximos Pasos - Instrucciones de Ejecución

### 1. Actualizar los Archivos del Proyecto

Reemplaza los archivos modificados:

```bash
cd d:\univercidad\micro\ servicios\microservicios

# Reemplazar el main.py de Departamentos
mv gestion-Departamentos\app\main_new.py gestion-Departamentos\app\main.py
```

### 2. Construir y Ejecutar el Stack

```bash
# Construir todas las imágenes
docker-compose build

# Ejecutar todos los contenedores
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

### 3. Esperar a que todos los servicios estén saludables

```bash
# Ver logs del servicio
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### 4. Acceder a los Dashboards

Una vez que Grafana esté saludable:

```
URL: http://localhost:3000
Usuario: admin
Contraseña: admin
```

---

## 🔍 Verificación Rápida

### Health Check de Servicios

```bash
# Empleados
curl http://localhost:8080/actuator/health

# Departamentos  
curl http://localhost:8081/health

# Notificaciones
curl http://localhost:8082/health

# Autenticación
curl http://localhost:8084/health

# Perfiles
curl http://localhost:8083/api/health
```

### Métricas de Prometheus

```bash
# Empleados (Spring Boot Actuator)
curl http://localhost:8080/actuator/prometheus

# Departamentos (Prometheus client)
curl http://localhost:8081/metrics

# Notificaciones
curl http://localhost:8082/metrics
```

### Prometheus UI

```
URL: http://localhost:9090
Ir a Status > Targets para ver todos los servicios siendo scrapeados
```

### Zipkin (Trazas Distribuidas)

```
URL: http://localhost:9411
Buscar trazas por servicio
```

### Loki (Logs)

```
URL: http://localhost:3100/api/labels
Este es solo el API, ver logs en Grafana Explorer
```

---

## 📊 Dashboards Disponibles

### Dashboard 1: "Microservices Health & Performance"
**Ubicación**: Grafana > Dashboards > Observability > Microservices Health & Performance

**Paneles**:
1. **Services Health Status** - Pie chart de servicios UP/DOWN
2. **Individual Service Status** - Estado individual de cada servicio
3. **Request Rate** - Solicitudes por segundo
4. **Request Latency Percentiles** - P50, P95, P99 en ms
5. **Error Rate** - Tasa de errores 4xx/5xx

### Dashboard 2: "Logs & Traces Explorer"
**Ubicación**: Grafana > Dashboards > Observability > Logs & Traces Explorer

**Paneles**:
1. **Log Volume by Service** - Volumen de logs por servicio
2. **Log Level Distribution** - ERROR, WARN, INFO
3. **Error Logs** - Logs con nivel ERROR
4. **Service Logs** - Todos los logs estructurados

---

## 🔧 Configuración Detallada

### Prometheus Scraping

Todos los servicios son scrapeados cada 15 segundos por Prometheus.

**Archivo de configuración**: `observability/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

### OpenTelemetry Tracing

Todos los servicios envían trazas a Zipkin en formato HTTP/Protobuf.

**Configuración (Java)**:
```yaml
otel:
  exporter:
    otlp:
      endpoint: http://zipkin:9411
  service:
    name: service-name
```

### Log Collection

Promtail recolecta logs de los contenedores Docker y los envía a Loki.

**Ubicación**: `observability/promtail-config.yml`

---

## 🧪 Pruebas (Fase 5)

### Generar Tráfico

```bash
# Opción 1: Script PowerShell
$env:EMPLOYEES_API="http://localhost:8080"
for ($i = 0; $i -lt 100; $i++) {
    curl -X POST "$env:EMPLOYEES_API/api/v1/empleados" `
        -H "Content-Type: application/json" `
        -d '{"nombre":"Test","apellido":"User"}'
    Start-Sleep -Milliseconds 100
}

# Opción 2: Usar el CLI curl en loop
for i in {1..100}; do
    curl -X POST "http://localhost:8080/api/v1/empleados" \
        -H "Content-Type: application/json" \
        -d '{"nombre":"Test","apellido":"User"}'
done
```

### Simular Falla

```bash
# Detener un servicio
docker-compose stop empleados-service

# Ver que el dashboard cambie a rojo
# Esperar 30 segundos para que se refleje

# Reiniciar el servicio
docker-compose start empleados-service
```

### Inducir Latencia

Modificar el controller de empleados para agregar retrasos:

```java
@GetMapping("/api/v1/empleados")
public ResponseEntity<?> getEmpleados() {
    try {
        Thread.sleep(2000); // 2 segundos de latencia
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
    return ResponseEntity.ok(empleadoService.getAllEmpleados());
}
```

---

## 📝 Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| `prometheus.yml` | Configuración de scraping |
| `loki-config.yml` | Configuración de Loki |
| `promtail-config.yml` | Configuración de Promtail |
| `grafana-datasources.json` | Datasources de Grafana |
| `grafana-dashboards-provider.json` | Provider de dashboards |
| `dashboards/microservices-overview.json` | Dashboard principal |
| `dashboards/logs-traces-explorer.json` | Dashboard de logs |

---

## 🚨 Solución de Problemas

### Grafana no muestra datos

1. Verificar que Prometheus esté scrapeando:
   ```
   http://localhost:9090 > Status > Targets
   ```

2. Verificar datasources en Grafana:
   ```
   http://localhost:3000 > Administration > Data sources
   ```

3. Hacer una query en Prometheus:
   ```
   http://localhost:9090 > Graph
   Query: up
   ```

### Logs no aparecen en Loki

1. Verificar que Promtail esté corriendo:
   ```bash
   docker-compose logs promtail
   ```

2. Verificar que Loki esté accesible:
   ```bash
   curl http://localhost:3100/loki/api/v1/labels
   ```

### Trazas no aparecen en Zipkin

1. Verificar que OpenTelemetry está instrumentado
2. Verificar que Zipkin esté corriendo
3. Hacer una solicitud y esperar 5 segundos
4. Ir a http://localhost:9411

---

## 📚 Referencias

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Zipkin Tracing](https://zipkin.io/pages/architecture.html)
- [Loki Log Storage](https://grafana.com/docs/loki/latest/)
- [OpenTelemetry](https://opentelemetry.io/docs/)

---

## ✅ Checklist Final

- [ ] Docker Compose up sin errores
- [ ] Prometheus scrapeando todos los servicios
- [ ] Grafana dashboards mostrando datos
- [ ] Zipkin recibiendo trazas
- [ ] Loki almacenando logs
- [ ] Alertas configuradas en Grafana
- [ ] Notificaciones funcionando (Discord/Slack)
- [ ] Pruebas de caos completadas
- [ ] Documentación finalizada

