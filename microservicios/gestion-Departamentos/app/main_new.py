from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import time

# Cargar .env desde la raíz del proyecto (retos-microservicios/.env)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# ============================================
# OpenTelemetry Configuration
# ============================================
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Create OpenTelemetry resource
resource = Resource(attributes={
    SERVICE_NAME: "gestion-departamentos",
    "deployment.environment": "development",
    "service.namespace": "microservicios"
})

# Create Zipkin exporter
try:
    zipkin_exporter = ZipkinExporter(
        localip="0.0.0.0",
        port=9411,
        service_name="gestion-departamentos",
    )
    
    # Create and set tracer provider
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(SimpleSpanProcessor(zipkin_exporter))
    trace.set_tracer_provider(trace_provider)
except Exception as e:
    print(f"Warning: Could not configure Zipkin exporter: {e}")

# ============================================
# Structured JSON Logging Configuration
# ============================================
logger = logging.getLogger("gestion-departamentos")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.departamentos import router as departamentos_router
from app.core.security import validate_jwt_or_401

# ============================================
# Prometheus Metrics Configuration
# ============================================
from prometheus_client import make_asgi_app, Counter, Histogram

app = FastAPI(title="Servicio de Departamentos", version="1.0.0")

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Define custom metrics
request_count = Counter(
    'departamentos_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'departamentos_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Instrument FastAPI
try:
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
except Exception as e:
    print(f"Warning: Could not instrument FastAPI: {e}")


@app.middleware("http")
async def jwt_auth_middleware(request: Request, call_next):
    try:
        validate_jwt_or_401(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"campo": " -> ".join(str(l) for l in e["loc"][1:]), "error": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": "Datos de entrada inválidos", "errores": errors})

app.include_router(departamentos_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "UP",
        "service": "gestion-departamentos",
        "timestamp": time.time(),
        "checks": {
            "database": "UP",
            "http": "UP"
        }
    }

@app.get("/ready")
async def readiness_probe():
    """Readiness probe for Kubernetes/Docker health checks."""
    return {
        "ready": True,
        "service": "gestion-departamentos"
    }
