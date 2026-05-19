from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.departamento import DepartamentoCreate, DepartamentoOut
from app.services.departamento_service import create_departamento, get_departamento, list_departamentos

router = APIRouter(prefix="/departamentos", tags=["departamentos"])

@router.post("", response_model=DepartamentoOut, status_code=status.HTTP_201_CREATED)
def post_departamento(payload: DepartamentoCreate, db: Session = Depends(get_db)):
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
def get_departamento_by_id(dep_id: str, db: Session = Depends(get_db)):
    dep = get_departamento(db, dep_id)
    if not dep:
        raise HTTPException(status_code=404, detail=f"Departamento con id '{dep_id}' no existe")
    return dep

@router.get("", response_model=list[DepartamentoOut])
def get_departamentos(db: Session = Depends(get_db)):
    return list_departamentos(db)