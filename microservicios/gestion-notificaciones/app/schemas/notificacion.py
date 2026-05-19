from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificacionOut(BaseModel):
    id: str
    tipo: str
    destinatario: str
    mensaje: str
    fechaEnvio: datetime
    empleadoId: str

    model_config = ConfigDict(from_attributes=True)
