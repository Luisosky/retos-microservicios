from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.notificacion import NotificacionOut
from app.services.notificacion_service import (
    listar_notificaciones,
    listar_notificaciones_por_empleado,
)

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=list[NotificacionOut])
def get_notificaciones(db: Session = Depends(get_db)):
    return listar_notificaciones(db)


@router.get("/{empleado_id}", response_model=list[NotificacionOut])
def get_notificaciones_por_empleado(empleado_id: str, db: Session = Depends(get_db)):
    return listar_notificaciones_por_empleado(db, empleado_id)
