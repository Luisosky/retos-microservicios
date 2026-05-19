from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.notificacion import Notificacion


def crear_notificacion(
    db: Session,
    tipo: str,
    destinatario: str,
    mensaje: str,
    empleado_id: str,
) -> Notificacion:
    notificacion = Notificacion(
        tipo=tipo,
        destinatario=destinatario,
        mensaje=mensaje,
        fechaEnvio=datetime.now(timezone.utc),
        empleadoId=empleado_id,
    )
    db.add(notificacion)
    db.commit()
    db.refresh(notificacion)
    return notificacion


def listar_notificaciones(db: Session) -> list[Notificacion]:
    return db.query(Notificacion).order_by(Notificacion.fechaEnvio.desc()).all()


def listar_notificaciones_por_empleado(db: Session, empleado_id: str) -> list[Notificacion]:
    return (
        db.query(Notificacion)
        .filter(Notificacion.empleadoId == empleado_id)
        .order_by(Notificacion.fechaEnvio.desc())
        .all()
    )
