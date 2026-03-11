import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tipo: Mapped[str] = mapped_column(String(32), nullable=False)
    destinatario: Mapped[str] = mapped_column(String(255), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    fechaEnvio: Mapped[datetime] = mapped_column("fecha_envio", DateTime(timezone=True), nullable=False)
    empleadoId: Mapped[str] = mapped_column("empleado_id", String(64), nullable=False, index=True)
