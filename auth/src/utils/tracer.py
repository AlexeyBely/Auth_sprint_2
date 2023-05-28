from functools import wraps

from flask import request
from opentelemetry import trace as ot_trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from settings import api_settings


current_tracer = ot_trace.get_tracer(__name__)


def configure_tracer() -> None:
    ot_trace.set_tracer_provider(
        TracerProvider(
            resource=Resource(
                attributes={'service.name': 'auth-service'}
            )
        ))
    ot_trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=api_settings.jaeger_host,
                agent_port=api_settings.jaeger_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    ot_trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


def trace(func):
    @wraps(func)
    def inner(*args, **kwargs):
        with current_tracer.start_as_current_span('api-request'):
            request_id = request.headers.get('X-Request-Id')
            span = current_tracer.start_span(func.__name__)
            result = func(*args, **kwargs)
            span.set_attribute('http.request_id', request_id)
            span.end()
            return result
    return inner

