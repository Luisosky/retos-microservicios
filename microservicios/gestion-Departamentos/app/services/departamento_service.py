from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.departamento import Departamento
from app.schemas.departamento import DepartamentoCreate

def create_departamento(db: Session, data: DepartamentoCreate) -> Departamento:
    dep = Departamento(id=data.id, nombre=data.nombre, descripcion=data.descripcion)
    db.add(dep)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Ya existe un departamento con id '{data.id}'")
    db.refresh(dep)
    return dep

def get_departamento(db: Session, dep_id: str) -> Departamento | None:
    return db.get(Departamento, dep_id)

def delete_departamento(db: Session, dep_id: str) -> None:
    dep = db.get(Departamento, dep_id)
    if not dep:
        raise ValueError(f"Departamento con id '{dep_id}' no existe")
    db.delete(dep)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f"No se puede eliminar el departamento '{dep_id}' porque tiene empleados asociados")

def list_departamentos(db: Session) -> list[Departamento]:
    return db.query(Departamento).order_by(Departamento.nombre.asc()).all()