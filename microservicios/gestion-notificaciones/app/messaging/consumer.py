import json
import threading
import time

import pika

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.notificacion_service import crear_notificacion


class EmpleadoEventsConsumer:
    def __init__(self):
        self._thread = None
        self._stop_event = threading.Event()
        self._connected = False

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._connected = False

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive() and self._connected)

    def _run(self):
        while not self._stop_event.is_set():
            try:
                credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_pass)
                parameters = pika.ConnectionParameters(
                    host=settings.rabbitmq_host,
                    port=settings.rabbitmq_port,
                    credentials=credentials,
                    heartbeat=30,
                )
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()

                channel.exchange_declare(
                    exchange=settings.exchange_name,
                    exchange_type="topic",
                    durable=True,
                )
                channel.queue_declare(queue=settings.queue_name, durable=True)
                channel.queue_bind(
                    exchange=settings.exchange_name,
                    queue=settings.queue_name,
                    routing_key="empleado.creado",
                )
                channel.queue_bind(
                    exchange=settings.exchange_name,
                    queue=settings.queue_name,
                    routing_key="empleado.eliminado",
                )
                channel.queue_bind(
                    exchange=settings.exchange_name,
                    queue=settings.queue_name,
                    routing_key="usuario.creado",
                )
                channel.queue_bind(
                    exchange=settings.exchange_name,
                    queue=settings.queue_name,
                    routing_key="usuario.recuperacion",
                )

                def callback(ch, method, properties, body):
                    try:
                        payload = json.loads(body.decode("utf-8"))
                        if method.routing_key == "empleado.creado":
                            tipo = "BIENVENIDA"
                            destinatario = payload.get("email", "")
                            nombre = payload.get("nombre", "")
                            mensaje = f"Bienvenido {nombre}"
                            empleado_id = payload.get("id", "")
                        elif method.routing_key == "empleado.eliminado":
                            tipo = "DESVINCULACION"
                            destinatario = payload.get("email", "")
                            mensaje = "Su cuenta ha sido desvinculada"
                            empleado_id = payload.get("id", "")
                        elif method.routing_key in {"usuario.creado", "usuario.recuperacion"}:
                            tipo = "SEGURIDAD"
                            destinatario = payload.get("email", "")
                            token = payload.get("token", "")
                            mensaje = (
                                "Para establecer o recuperar su contrasena, utilice este token: "
                                f"{token}"
                            )
                            empleado_id = payload.get("id", "auth-security")
                        else:
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            return

                        print(
                            f"[NOTIFICACION] Tipo: {tipo} | Para: {destinatario} | Mensaje: \"{mensaje}\""
                        )

                        db = SessionLocal()
                        try:
                            crear_notificacion(
                                db,
                                tipo=tipo,
                                destinatario=destinatario,
                                mensaje=mensaje,
                                empleado_id=empleado_id,
                            )
                        finally:
                            db.close()

                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as exc:
                        print(f"[NOTIFICACION] Error procesando evento: {exc}")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                channel.basic_qos(prefetch_count=10)
                channel.basic_consume(queue=settings.queue_name, on_message_callback=callback)

                self._connected = True
                while not self._stop_event.is_set():
                    connection.process_data_events(time_limit=1)
                self._connected = False

                channel.close()
                connection.close()
            except Exception as exc:
                self._connected = False
                print(f"[NOTIFICACION] Error conectando a RabbitMQ: {exc}")
                time.sleep(5)
