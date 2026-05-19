from fastapi import APIRouter, Depends, HTTPException, status, Path
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
def get_notificaciones_por_empleado(
    empleado_id: str = Path(..., min_length=1, description="ID del empleado"),
    db: Session = Depends(get_db)
):
    if not empleado_id or not empleado_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID del empleado es requerido y no puede estar vacío"
        )
    return listar_notificaciones_por_empleado(db, empleado_id)
