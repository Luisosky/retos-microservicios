from pydantic import BaseModel, Field, field_validator

class DepartamentoBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(min_length=1)

    @field_validator("nombre", "descripcion", mode="before")
    @classmethod
    def no_blank(cls, v: str) -> str:
        if isinstance(v, str) and not v.strip():
            raise ValueError("el campo no puede estar vacío o contener solo espacios")
        return v

class DepartamentoCreate(DepartamentoBase):
    id: str = Field(min_length=1, max_length=64)

    @field_validator("id", mode="before")
    @classmethod
    def id_no_blank(cls, v: str) -> str:
        if isinstance(v, str) and not v.strip():
            raise ValueError("el campo no puede estar vacío o contener solo espacios")
        return v

class DepartamentoOut(DepartamentoCreate):
    pass