"""
Observabilidad: métricas Prometheus + trazas OpenTelemetry → Zipkin.
Se llama desde main.py con la app de FastAPI ya construida.
"""

from __future__ import annotations

import logging
import os
from typing import Iterable

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total de peticiones HTTP recibidas",
    ["service", "method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Latencia de peticiones HTTP en segundos",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)


def _excluded_from_metrics(path: str) -> bool:
    return path in ("/metrics", "/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico")


def install_metrics(app: FastAPI, service_name: str) -> None:
    """Middleware ligero que cuenta peticiones y latencia, y expone /metrics."""

    @app.middleware("http")
    async def _metrics_middleware(request: Request, call_next):
        path = request.url.path
        if _excluded_from_metrics(path):
            return await call_next(request)
        method = request.method
        with HTTP_REQUEST_DURATION_SECONDS.labels(
            service=service_name, method=method, path=path
        ).time():
            response = await call_next(request)
        HTTP_REQUESTS_TOTAL.labels(
            service=service_name,
            method=method,
            path=path,
            status=str(response.status_code),
        ).inc()
        return response

    @app.get("/metrics", include_in_schema=False)
    def _prom_metrics() -> Response:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def install_tracing(app: FastAPI, service_name: str) -> None:
    """Configura OpenTelemetry → Zipkin con propagación W3C tracecontext.

    Solo se activa si está disponible la URL del exportador. Falla silenciosa
    para no romper arranque si las libs OTel no están instaladas.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.zipkin.json import ZipkinExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.propagate import set_global_textmap
        from opentelemetry.propagators.composite import CompositePropagator
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.trace.propagation.tracecontext import (
            TraceContextTextMapPropagator,
        )
        from opentelemetry.baggage.propagation import W3CBaggagePropagator
    except ImportError:
        logging.getLogger(__name__).warning(
            "OpenTelemetry no instalado, trazas deshabilitadas para %s", service_name
        )
        return

    zipkin_endpoint = os.getenv(
        "OTEL_EXPORTER_ZIPKIN_ENDPOINT", "http://zipkin:9411/api/v2/spans"
    )

    resource = Resource.create({SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(ZipkinExporter(endpoint=zipkin_endpoint))
    )
    trace.set_tracer_provider(provider)

    set_global_textmap(
        CompositePropagator(
            [TraceContextTextMapPropagator(), W3CBaggagePropagator()]
        )
    )

    FastAPIInstrumentor.instrument_app(app, excluded_urls="/metrics,/health")
    RequestsInstrumentor().instrument()

    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument()
    except ImportError:
        pass


def install_json_logging(service_name: str, extra_excluded: Iterable[str] = ()) -> None:
    """Reemplaza el formatter raíz con uno JSON y añade traceId si hay span activo."""
    try:
        from pythonjsonlogger import jsonlogger
    except ImportError:
        return

    class _OtelJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):  # type: ignore[override]
            super().add_fields(log_record, record, message_dict)
            log_record.setdefault("service", service_name)
            log_record.setdefault("level", record.levelname)
            log_record.setdefault("timestamp", self.formatTime(record, self.datefmt))
            try:
                from opentelemetry.trace import get_current_span

                span = get_current_span()
                ctx = span.get_span_context() if span else None
                if ctx and ctx.trace_id:
                    log_record.setdefault("traceId", format(ctx.trace_id, "032x"))
                    log_record.setdefault("spanId", format(ctx.span_id, "016x"))
            except Exception:
                pass

    formatter = _OtelJsonFormatter(
        "%(timestamp)s %(level)s %(service)s %(name)s %(message)s"
    )

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

    # Silenciar accesos a /metrics y /health en el log
    class _MetricsAccessFilter(logging.Filter):
        excluded = {"/metrics", "/health", *extra_excluded}

        def filter(self, record: logging.LogRecord) -> bool:
            msg = record.getMessage()
            return not any(p in msg for p in self.excluded)

    logging.getLogger("uvicorn.access").addFilter(_MetricsAccessFilter())
