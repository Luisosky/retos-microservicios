from pydantic import BaseModel, Field

class DepartamentoBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(min_length=1)

class DepartamentoCreate(DepartamentoBase):
    id: str = Field(min_length=1, max_length=64)

class DepartamentoOut(DepartamentoCreate):
    pass