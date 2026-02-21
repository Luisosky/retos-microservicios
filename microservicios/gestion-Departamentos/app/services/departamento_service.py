from sqlalchemy.orm import Session
from app.models.departamento import Departamento
from app.schemas.departamento import DepartamentoCreate

def create_departamento(db: Session, data: DepartamentoCreate) -> Departamento:
    dep = Departamento(id=data.id, nombre=data.nombre, descripcion=data.descripcion)
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return dep

def get_departamento(db: Session, dep_id: str) -> Departamento | None:
    return db.get(Departamento, dep_id)

def list_departamentos(db: Session) -> list[Departamento]:
    return db.query(Departamento).order_by(Departamento.nombre.asc()).all()