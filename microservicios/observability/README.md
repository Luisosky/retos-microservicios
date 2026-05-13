# 📊 Observability Setup Guide

This directory contains all configurations for the observability stack: Prometheus, Grafana, Zipkin, Loki, and Promtail.

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `prometheus.yml` | Prometheus scrape configuration for all microservices |
| `loki-config.yml` | Loki log storage configuration |
| `promtail-config.yml` | Promtail log collection configuration |
| `grafana-datasources.json` | Grafana datasources provisioning |
| `grafana-dashboards-provider.json` | Grafana dashboard provider configuration |
| `dashboards/` | Directory containing Grafana dashboard JSON definitions |

## 🚀 Service Instrumentation Checklist

### ✅ Empleados (Java/Spring Boot)
- [x] Added `spring-boot-starter-actuator` dependency
- [x] Added `micrometer-registry-prometheus` dependency
- [x] Added OpenTelemetry SDK and Zipkin exporter
- [x] Configured Actuator endpoints in `application.yml`
- [x] Metrics exposed at `/actuator/prometheus`
- [x] Health check at `/actuator/health`
- [ ] Custom business metrics (TODO in Phase 3 completion)

### ✅ Departamentos (Python/FastAPI)
- [x] Added `prometheus-client` to requirements.txt
- [x] Added OpenTelemetry libraries
- [x] Updated main.py with PrometheusMiddleware
- [x] Health check at `/health` (extended)
- [x] Metrics endpoint at `/metrics`
- [ ] Database connection pool monitoring (TODO)

### ✅ Notificaciones (Python/FastAPI)
- [x] Added observability dependencies to requirements.txt
- [ ] Need to update main.py with instrumentation
- [ ] Add health endpoint

### ⏳ Autenticación (C#/.NET Core)
- [ ] Add `prometheus-net` NuGet package
- [ ] Configure Prometheus middleware
- [ ] Add health check endpoint
- [ ] Configure OpenTelemetry exporter

### ⏳ Perfiles (PHP/Laravel)
- [ ] Add `prometheus-community/laravel` Composer package
- [ ] Register middleware
- [ ] Add health endpoint
- [ ] Configure OpenTelemetry (via PECL)

---

## 📊 Metrics Exposed

Each microservice exposes metrics in Prometheus format at the following endpoints:

| Service | Endpoint | Scrape Interval |
|---------|----------|-----------------|
| empleados-service | `http://empleados-service:8080/actuator/prometheus` | 15s |
| departamentos | `http://departamentos:8081/metrics` | 15s |
| notificaciones | `http://notificaciones:8082/metrics` | 15s |
| autenticacion | `http://autenticacion:8084/metrics` | 15s |
| perfiles | `http://perfiles:8083/metrics` | 15s |

---

## 🏥 Health Checks

All services implement health check endpoints for Docker and Kubernetes probes:

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

---

## 🔀 Distributed Tracing

All services are configured to send traces to Zipkin:

- **Zipkin UI**: http://localhost:9411
- **Trace Sampling**: `always_on` (development mode)
- **Sampling Rate**: 100% of traces collected
- **Batch Size**: Default (depends on OpenTelemetry SDK)

### View Traces:

1. Open http://localhost:9411
2. Click "Find Traces"
3. Select a service from the dropdown
4. Click "Find Traces"

---

## 📝 Log Aggregation

All container logs are collected by Promtail and stored in Loki:

- **Loki API**: http://loki:3100
- **Log Query Language**: LogQL (similar to PromQL)
- **Retention**: 30 days (configurable in `loki-config.yml`)

### Query Logs in Grafana:

1. Open http://localhost:3000/explore
2. Select "Loki" datasource
3. Use LogQL queries like:
   ```logql
   {service="empleados"} | json | severity="ERROR"
   ```

---

## 📈 Dashboards

Main dashboards available in Grafana:

| Dashboard | Description |
|-----------|------------|
| System Overview | CPU, Memory, Requests (all services) |
| Microservices Health | Health status and response times |
| Request Analytics | Request rate, latency, errors |
| Distributed Traces | Trace comparison and analysis |
| Logs Explorer | Structured log search |

---

## 🚨 Alerts

Pre-configured alerts in Grafana:

| Alert | Condition | Action |
|-------|-----------|--------|
| Service Down | Any service `/health` returns non-200 | Discord webhook |
| High Latency | P99 latency > 1000ms for 5 minutes | Discord webhook |
| Error Rate High | Error rate > 5% for 5 minutes | Discord webhook |
| Memory Usage | Memory usage > 80% for service | Discord webhook |

---

## 🔧 Configuration Reference

### Prometheus Scrape Configuration

```yaml
global:
  scrape_interval: 15s      # Default scrape interval
  evaluation_interval: 15s  # How often to check alert rules
```

### OpenTelemetry Configuration

```yaml
otel:
  traces:
    sampler: always_on  # Use parentbased_probabilistic for production
  exporter:
    otlp:
      endpoint: http://zipkin:9411
  service:
    name: service-name
    version: 1.0.0
```

### Loki Configuration

```yaml
ingester:
  chunk_idle_period: 3m      # How long to keep a chunk in memory
  chunk_retain_period: 1m    # How long to retain chunks after flush
  max_chunk_age: 1h          # Maximum age of chunk before flush
```

---

## 🐛 Troubleshooting

### Prometheus Not Scraping

Check `/actuator/prometheus` endpoint manually:
```bash
curl http://localhost:8080/actuator/prometheus
```

If returning 404, verify:
- Actuator dependencies are added
- Endpoint is configured in `application.yml`
- Container is running and healthy

### No Traces Appearing in Zipkin

Ensure:
- OpenTelemetry libraries are imported
- Zipkin exporter is configured with correct endpoint
- Instrumentation is called at app startup
- Trace provider is set globally

### Logs Not Appearing in Loki

Verify:
- Promtail is running (`docker ps | grep promtail`)
- Docker socket is mounted correctly
- Promtail config points to correct Loki endpoint
- Container logs are being written to stdout/stderr

---

## 📚 References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/)
- [Zipkin Documentation](https://zipkin.io/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Grafana Documentation](https://grafana.com/docs/grafana/)

---

## 🎯 Next Steps

1. **Phase 3 Completion**: Finish instrumenting remaining services (C#, PHP)
2. **Phase 4**: Create Grafana dashboards with custom metrics
3. **Phase 5**: Run chaos tests to validate monitoring
4. **Phase 6**: Analyze traces and document findings
