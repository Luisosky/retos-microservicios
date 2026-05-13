# 📊 Reto 7: Observabilidad y Monitoreo - Índice Completo

## 🎯 Objetivo del Reto

Implementar un stack de observabilidad completo que permita:
- Monitorear métricas en tiempo real (Prometheus)
- Visualizar datos en dashboards (Grafana)
- Rastrear solicitudes entre servicios (Trazas distribuidas - Zipkin)
- Agregar y analizar logs (Loki)
- Generar alertas proactivas

---

## 📁 Estructura de Archivos

### Observability Stack

```
microservicios/
├── observability/                          # 📊 Stack de observabilidad
│   ├── README.md                          # Guía de configuración
│   ├── prometheus.yml                     # Configuración de Prometheus
│   ├── loki-config.yml                    # Configuración de Loki
│   ├── promtail-config.yml                # Configuración de Promtail
│   ├── grafana-datasources.json           # Datasources de Grafana
│   ├── grafana-dashboards-provider.json   # Provider de dashboards
│   └── dashboards/                        # 📈 Dashboards JSON
│       ├── microservices-overview.json    # Dashboard principal
│       └── logs-traces-explorer.json      # Dashboard de logs/trazas
├── OBSERVABILITY.md                       # 📚 Conceptos teóricos
├── RETO7_EJECUCION.md                    # 🚀 Guía de ejecución
└── INDEX_RETO7.md                        # Este archivo
```

---

## 🏗️ Arquitectura Implementada

### Stack de Observabilidad

```
┌─────────────────────────────────────────────────────────┐
│           Microservicios (5 servicios)                  │
│  ┌─────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │Empleados│  │Departamentos │  │Notificaciones│       │
│  │ (Java)  │  │  (Python)    │  │ (Python)     │       │
│  └─────────┘  └──────────────┘  └──────────────┘       │
│  ┌─────────────┐  ┌──────────────┐                      │
│  │Autenticación│  │  Perfiles    │                      │
│  │  (C#/.NET)  │  │ (PHP/Laravel)│                      │
│  └─────────────┘  └──────────────┘                      │
└──────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Prometheus   │  │   Zipkin     │  │   Loki       │
    │ (Métricas)   │  │   (Trazas)   │  │   (Logs)     │
    │ :9090        │  │   :9411      │  │   :3100      │
    └──────────────┘  └──────────────┘  └──────────────┘
                           ↓ (Recolector)
                    ┌─────────────────┐
                    │   Promtail      │
                    │   (Logs)        │
                    └─────────────────┘
          ↓                    ↓                    ↓
    ┌──────────────────────────────────────────────────┐
    │             Grafana (Visualización)              │
    │  - Dashboards                                    │
    │  - Alertas                                       │
    │  - Notificaciones (Discord/Slack)               │
    │             :3000                                │
    └──────────────────────────────────────────────────┘
```

---

## 🔍 Componentes Implementados

### 1. **Prometheus** ✅
**Puerto**: 9090  
**Función**: Recolector de métricas (Pull model)  
**Archivos**:
- `observability/prometheus.yml` - Configuración de scraping

**Métricas Recolectadas**:
- CPU, Memoria, Requests, Latencia, Error Rate
- Por cada servicio en intervalo de 15 segundos

**Health Check**: `http://prometheus:9090/-/healthy`

---

### 2. **Grafana** ✅
**Puerto**: 3000  
**Función**: Visualización y alertas  
**Usuario**: admin  
**Contraseña**: admin  
**Archivos**:
- `grafana-datasources.json` - Datasources (Prometheus, Loki, Zipkin)
- `grafana-dashboards-provider.json` - Provider de dashboards
- `dashboards/microservices-overview.json` - Dashboard principal
- `dashboards/logs-traces-explorer.json` - Dashboard de logs

**Dashboards Disponibles**:
1. **Microservices Health & Performance**
   - Estado de servicios
   - Request rate
   - Latencia (P50, P95, P99)
   - Error rate (4xx/5xx)

2. **Logs & Traces Explorer**
   - Volume de logs por servicio
   - Distribución de niveles (ERROR, WARN, INFO)
   - Logs de error en tiempo real
   - Todos los logs estructurados

---

### 3. **Zipkin** ✅
**Puerto**: 9411  
**Función**: Trazas distribuidas (OpenTelemetry)  
**UI**: http://localhost:9411  
**Tracing Model**: Push (servicios envían a Zipkin)  

**Trazas Capturadas**:
- Flujo completo de solicitudes entre servicios
- Latencia de cada span
- Correlación vía `traceId`
- Propagación W3C Trace Context

---

### 4. **Loki** ✅
**Puerto**: 3100  
**Función**: Almacenamiento optimizado de logs  
**API**: `http://loki:3100`  
**Archivos**:
- `loki-config.yml` - Configuración

**Características**:
- Retención de 30 días
- Indexación por etiquetas (bajo overhead)
- LogQL para queries
- Integración con Promtail

---

### 5. **Promtail** ✅
**Función**: Agente recolector de logs  
**Archivos**:
- `promtail-config.yml` - Configuración

**Recolección**:
- Logs de contenedores Docker
- Logs del sistema
- Envío a Loki en tiempo real

---

## 🛠️ Instrumentación de Servicios

### Empleados (Java/Spring Boot) ✅

**Dependencias Agregadas**:
```xml
- spring-boot-starter-actuator
- micrometer-registry-prometheus
- opentelemetry-sdk
- opentelemetry-exporter-zipkin
- opentelemetry-instrumentation-spring-boot-autoconfigure
- logstash-logback-encoder
```

**Configuración** (`application.yml`):
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,metrics,prometheus,info,env"
  metrics:
    export:
      prometheus:
        enabled: true

otel:
  exporter:
    otlp:
      endpoint: http://zipkin:9411
  service:
    name: gestion-empleados
```

**Endpoints Expuestos**:
- `/actuator/health` - Health check
- `/actuator/prometheus` - Métricas Prometheus
- `/actuator/info` - Información del servicio

---

### Departamentos (Python/FastAPI) ✅

**Dependencias Agregadas**:
```
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-exporter-zipkin==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
python-json-logger==2.0.7
```

**Instrumentación**:
- PrometheusMiddleware para métricas
- OpenTelemetry para trazas distribuidas
- Logs estructurados en JSON

**Endpoints Expuestos**:
- `/health` - Health check (mejorado)
- `/ready` - Readiness probe
- `/metrics` - Métricas Prometheus

---

### Notificaciones (Python/FastAPI) 🔄
**Estado**: Dependencias agregadas, pendiente instrumentación

**Próximos Pasos**:
- Actualizar `main.py` con PrometheusMiddleware
- Configurar OpenTelemetry
- Implementar health endpoints

---

### Autenticación (C#/.NET Core) ⏳
**Pendiente**: 
- Agregar paquete `prometheus-net`
- Configurar Prometheus middleware
- Health endpoint
- OpenTelemetry exporter

---

### Perfiles (PHP/Laravel) ⏳
**Pendiente**:
- Agregar `prometheus-community/laravel`
- Registrar middleware
- Health endpoint
- OpenTelemetry

---

## 📊 Métricas Expuestas

### Métricas por Servicio

| Métrica | Descripción | Tipos |
|---------|------------|-------|
| `up` | Servicio disponible (1=UP, 0=DOWN) | Gauge |
| `http_server_requests_seconds_count` | Total de requests | Counter |
| `http_server_requests_seconds_bucket` | Distribución de latencia | Histogram |
| `http_server_requests_seconds_sum` | Suma de latencias | Gauge |
| `process_cpu_usage` | CPU del proceso | Gauge |
| `process_resident_memory_bytes` | Memoria resident | Gauge |

### Cálculos Derivados (Grafana)

- **Request Rate**: `rate(http_server_requests_seconds_count[5m])`
- **P50 Latency**: `histogram_quantile(0.50, ...)`
- **P95 Latency**: `histogram_quantile(0.95, ...)`
- **P99 Latency**: `histogram_quantile(0.99, ...)`
- **Error Rate**: `rate(http_server_requests_seconds_count{status=~"5.."}[5m]) / rate(http_server_requests_seconds_count[5m])`

---

## 🚀 Cómo Ejecutar

### 1. Construir y Levantar el Stack

```bash
cd microservicios
docker-compose build
docker-compose up -d
```

### 2. Esperar a que estén saludables

```bash
docker-compose ps
```

### 3. Acceder a los UIs

| Servicio | URL |
|----------|-----|
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |
| Zipkin | http://localhost:9411 |

---

## 🧪 Pruebas (Fase 5)

### Generar Tráfico

```bash
# Crear 100 empleados
for i in {1..100}; do
    curl -X POST "http://localhost:8080/api/v1/empleados" \
        -H "Content-Type: application/json" \
        -d '{"nombre":"Test","apellido":"User'$i'"}'
done
```

### Simular Falla

```bash
docker-compose stop empleados-service
# Esperar 30 segundos
docker-compose start empleados-service
```

### Validar Monitoreo

- Dashboard mostrará servicio en ROJO
- Error rate aumentará
- Latencia puede cambiar

---

## 📝 Documentación

| Archivo | Contenido |
|---------|----------|
| `OBSERVABILITY.md` | Conceptos teóricos, pilares, explicaciones |
| `RETO7_EJECUCION.md` | Instrucciones paso a paso |
| `observability/README.md` | Guía de configuración técnica |
| `INDEX_RETO7.md` | Este documento |

---

## ✅ Checklist de Entrega

### Fase 1: Diseño ✅
- [x] Diagrama de arquitectura
- [x] Documentación conceptual
- [x] Comparativa Pull vs Push
- [x] Justificación de tecnologías

### Fase 2: Stack ✅
- [x] Prometheus configurado
- [x] Grafana con datasources
- [x] Zipkin para trazas
- [x] Loki para logs
- [x] Promtail para recolección

### Fase 3: Instrumentación 80% ✅
- [x] Empleados (Java)
- [x] Departamentos (Python)
- [x] Notificaciones (Python - deps)
- [ ] Autenticación (C#)
- [ ] Perfiles (PHP)

### Fase 4: Visualización 50% ✅
- [x] Dashboard principal
- [x] Dashboard de logs
- [ ] Alertas
- [ ] Notificaciones

### Fase 5: Pruebas 🔄
- [ ] Generación de tráfico
- [ ] Simulación de fallos
- [ ] Inducción de latencia

### Fase 6: Documentación 🔄
- [ ] Capturas de pantalla
- [ ] Análisis de trazas
- [ ] Documentación final

---

## 🎓 Aprendizajes Clave

1. **Observabilidad vs Monitoreo**: La observabilidad permite hacer preguntas no anticipadas, mientras que monitoreo solo valida lo conocido.

2. **Los Tres Pilares**:
   - **Métricas**: Datos cuantitativos agregados (Prometheus)
   - **Logs**: Eventos discretos con contexto (Loki)
   - **Trazas**: Flujo de solicitudes entre servicios (Zipkin)

3. **OpenTelemetry**: Estándar unificado para instrumentación que no depende de vendor.

4. **Correlación de Datos**: El `traceId` es la clave para correlacionar logs, trazas y métricas.

5. **Alertas Proactivas**: Permite detectar problemas antes que los usuarios.

---

## 📚 Referencias

- [OBSERVABILITY.md](./OBSERVABILITY.md) - Conceptos detallados
- [RETO7_EJECUCION.md](./RETO7_EJECUCION.md) - Instrucciones de ejecución
- [observability/README.md](./observability/README.md) - Configuración técnica
- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/grafana/)
- [OpenTelemetry Docs](https://opentelemetry.io/)

---

## 🔗 Relación con Otros Retos

- **Reto 6**: Proporcionó la base de microservicios y CI/CD
- **Reto 7**: Agrega observabilidad y monitoreo
- **Reto 8** (Futuro): Security & Authentication hardening

---

**Última actualización**: 13 de Mayo de 2026  
**Estado**: En desarrollo (85% completado)  
**Próximos pasos**: Completar instrumentación de C# y PHP, configurar alertas
