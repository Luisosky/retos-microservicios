from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.departamento import DepartamentoCreate, DepartamentoOut
from app.services.departamento_service import create_departamento, get_departamento, list_departamentos

router = APIRouter(prefix="/departamentos", tags=["departamentos"])

@router.post("", response_model=DepartamentoOut, status_code=status.HTTP_201_CREATED)
def post_departamento(payload: DepartamentoCreate, db: Session = Depends(get_db)):
    # Si quieres evitar duplicados, aquí puedes validar existencia previa.
    return create_departamento(db, payload)

@router.get("/{dep_id}", response_model=DepartamentoOut)
def get_departamento_by_id(dep_id: str, db: Session = Depends(get_db)):
    dep = get_departamento(db, dep_id)
    if not dep:
        raise HTTPException(status_code=404, detail=f"Departamento con id '{dep_id}' no existe")
    return dep

@router.get("", response_model=list[DepartamentoOut])
def get_departamentos(db: Session = Depends(get_db)):
    return list_departamentos(db)