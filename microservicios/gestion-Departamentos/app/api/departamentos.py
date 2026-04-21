from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_dep001_or_403
from app.schemas.departamento import DepartamentoCreate, DepartamentoOut
from app.services.departamento_service import (
    create_departamento,
    get_departamento,
    list_departamentos,
    delete_departamento,
)

router = APIRouter(prefix="/departamentos", tags=["departamentos"])

@router.post("", response_model=DepartamentoOut, status_code=status.HTTP_201_CREATED)
def post_departamento(
    payload: DepartamentoCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_dep001_or_403),
):
    if get_departamento(db, payload.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un departamento con id '{payload.id}'"
        )
    try:
        return create_departamento(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{dep_id}", response_model=DepartamentoOut)
def get_departamento_by_id(
    dep_id: str = Path(..., min_length=1, description="ID del departamento"),
    db: Session = Depends(get_db)
):
    if not dep_id or not dep_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID del departamento es requerido y no puede estar vacío"
        )
    dep = get_departamento(db, dep_id)
    if not dep:
        raise HTTPException(status_code=404, detail=f"Departamento con id '{dep_id}' no existe")
    return dep

@router.delete("/{dep_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_departamento_by_id(
    dep_id: str = Path(..., min_length=1, description="ID del departamento a eliminar"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_dep001_or_403),
):
    if not dep_id or not dep_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID del departamento es requerido y no puede estar vacío"
        )
    dep = get_departamento(db, dep_id)
    if not dep:
        raise HTTPException(status_code=404, detail=f"Departamento con id '{dep_id}' no existe")
    try:
        delete_departamento(db, dep_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=list[DepartamentoOut])
def get_departamentos(db: Session = Depends(get_db)):
    return list_departamentos(db)