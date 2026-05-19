# 📊 Reto 7: Observabilidad y Monitoreo

## 🎯 Introducción a la Observabilidad

La **observabilidad** es la capacidad de entender el estado interno de un sistema analizando sus salidas externas (datos). Diferente del **monitoreo**, que es reactivo, la observabilidad es **proactiva** y permite responder preguntas no anticipadas sobre el comportamiento del sistema.

### ¿Qué es Monitoreo vs. Observabilidad?

| Aspecto | Monitoreo | Observabilidad |
|--------|-----------|-----------------|
| Enfoque | Reactivo | Proactivo |
| Preguntas | "¿Cuáles son los problemas conocidos?" | "¿Por qué ocurren los problemas?" |
| Datos | Métricas predefinidas | Logs, Trazas, Métricas (cualquier dato) |
| Escalabilidad | Limitado (reglas explícitas) | Ilimitado (correlación de datos) |
| Complejidad | Baja | Media-Alta |

---

## 🏛️ Los Tres Pilares de la Observabilidad

### 1. 📈 **Métricas (Metrics)**

**Definición**: Series temporales de datos numéricos que miden el estado del sistema.

**Características**:
- Valores cuantitativos (números)
- Agregados (sumas, promedios)
- Bajo consumo de almacenamiento
- Ideales para alertas en tiempo real

**Ejemplos**:
- CPU usage: 65%
- Memoria RAM: 2.5GB
- Requests per second: 1500 req/s
- Error rate: 0.5%
- Latencia P99: 250ms

**Herramienta**: **Prometheus**
- Modelo PULL: Los servidores recolectan datos de los servicios (`/metrics`)
- Scrape interval: 15 segundos (configurable)
- Retención de datos: 15 días (por defecto)

---

### 2. 📝 **Logs (Logs)**

**Definición**: Registros de eventos discretos con contexto textual detallado.

**Características**:
- Texto estructurado o no estructurado
- Información detallada de eventos
- Alto consumo de almacenamiento (optimizado con JSON)
- Excelentes para debugging

**Ejemplos**:
```json
{
  "timestamp": "2026-05-13T10:30:45.123Z",
  "level": "ERROR",
  "service": "empleados-service",
  "message": "Database connection failed",
  "traceId": "abc123def456",
  "userId": "user-42",
  "metadata": {
    "database": "mongodb",
    "timeout": 5000
  }
}
```

**Herramienta**: **Loki + Promtail**
- Loki: Almacenamiento optimizado de logs
- Promtail: Agente que recolecta logs de Docker
- LogQL: Lenguaje de query similar a PromQL

---

### 3. 🔀 **Trazas Distribuidas (Distributed Traces)**

**Definición**: Flujo completo de una solicitud a través de múltiples servicios.

**Características**:
- Visualiza cómo fluye una solicitud
- Identifica cuellos de botella
- Correlaciona eventos entre servicios
- Esencial en microservicios

**Ejemplo de Traza**:
```
User Request (T=0ms)
  ├─ API Gateway (0-5ms)
  ├─ Empleados Service (5-50ms)
  │  ├─ MongoDB Query (10-30ms)
  │  └─ Redis Cache (30-40ms)
  ├─ Departamentos Service (50-80ms)
  │  └─ PostgreSQL Query (55-75ms)
  └─ Response (T=80ms)
```

**Herramientas**: 
- **Zipkin** (Puerto 9411) - Más simple, ligero
- **Jaeger** (Puerto 16686) - Más potente, de Uber

**W3C Trace Context**:
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
                ─────────────────────────────────────────── TraceID
                                           ──────────────────── SpanID
```

---

## 🔄 Modelo PULL vs. PUSH

### PULL Model (Prometheus - ✅ Elegido)

**Cómo funciona**:
```
Prometheus Server → (Scrape) → Servicio:9090/metrics
```

**Ventajas**:
✅ Fácil debugging (acceso HTTP directo)  
✅ Menos sobrecarga de red  
✅ Control centralizado  
✅ Mejor para sistemas internos  

**Desventajas**:
❌ Requiere conectividad bidireccional  
❌ No ideal para clientes efímeros (Lambdas)  

---

### PUSH Model (OpenTelemetry/Zipkin - Complementario)

**Cómo funciona**:
```
Servicio → (Push) → Zipkin Collector:9411
```

**Ventajas**:
✅ Ideal para servidores sin IP fija  
✅ Máx. flexibilidad  
✅ Compatible con serverless  

**Desventajas**:
❌ Mayor sobrecarga de red  
❌ Más complejo de debuggear  

---

## 🌐 OpenTelemetry: Estándar Unificado

**¿Qué es OpenTelemetry (OTel)?**

OpenTelemetry es un estándar abierto que define cómo instrumentar, generar y recopilar datos de observabilidad (trazas, métricas, logs).

### Arquitectura OTel:

```
┌──────────────────────────────────────────┐
│          Aplicación                      │
│  ┌──────────────────────────────────────┐│
│  │    OpenTelemetry SDK (Instrumentos)   ││
│  │  - Tracing API                        ││
│  │  - Metrics API                        ││
│  │  - Logs API                           ││
│  └──────────────────────────────────────┘│
└──────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│      OpenTelemetry Exporter              │
│  (OTLP, Prometheus, Jaeger, etc)        │
└──────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│    Backend (Prometheus, Zipkin, Loki)   │
└──────────────────────────────────────────┘
```

### Componentes Clave:

| Componente | Función | Tecnología |
|-----------|---------|------------|
| **SDK (Software Development Kit)** | Librería de instrumentación | `opentelemetry-sdk-java`, `opentelemetry-sdk-python` |
| **Tracer** | Crea Spans (operaciones) | Context propagation (W3C) |
| **Exporter** | Envía datos al backend | gRPC OTLP, HTTP JSON |
| **Sampler** | Decide qué trazas registrar | AlwaysOn (desarrollo), Probabilistic (producción) |

---

## 🏗️ Stack de Observabilidad Elegido

### Por qué **Prometheus + Zipkin + Loki + Grafana**:

| Herramienta | Rol | Razón |
|-------------|-----|-------|
| **Prometheus** | Métricas (PULL) | Estándar de facto, CNCF, fácil escalabilidad |
| **Zipkin** | Trazas Distribuidas | Simplicidad, bajo overhead, UI intuitiva |
| **Loki** | Almacenamiento de Logs | Optimizado para etiquetas, bajo costo |
| **Promtail** | Recolector de Logs | Integración nativa con Docker, bajo overhead |
| **Grafana** | Visualización | Unificada, alerts, plugins ricos |

### Alternativas Evaluadas:

- **Jaeger vs Zipkin**: Zipkin es más ligero y suficiente para este reto
- **ELK vs Loki**: Loki es 10x más eficiente para volúmenes pequenos-medianos
- **DataDog vs Stack Abierto**: Stack abierto = aprendizaje profundo, sin costos

---

## 📋 Correlación de Datos: El Poder de la Observabilidad

**Ejemplo Real**: *¿Por qué tardó 5 segundos la solicitud?*

Sin correlación:
```
❌ Ver que P99 latency = 5s en Prometheus
❌ Ver error en logs de Empleados
❌ Ver lentitud en PostgreSQL sin context
= CONFUSIÓN
```

Con correlación vía `traceId`:
```
✅ Métrica: P99 latency = 5s en Prometheus
✅ Traza: Empleados→Departamentos→BD
✅ Log: "PostgreSQL query=3s traceId=abc123"
= CONCLUSIÓN: PostgreSQL fue el cuello de botella
```

---

## 🚀 Próximos Pasos

1. **Fase 2**: Desplegar el stack de observabilidad en Docker
2. **Fase 3**: Instrumentar microservicios
3. **Fase 4**: Crear dashboards y alertas
4. **Fase 5**: Validar con pruebas de caos
5. **Fase 6**: Documentar hallazgos

---

## 📚 Referencias

- [OpenTelemetry Docs](https://opentelemetry.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Zipkin Architecture](https://zipkin.io/pages/architecture.html)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Loki Documentation](https://grafana.com/docs/loki/)
