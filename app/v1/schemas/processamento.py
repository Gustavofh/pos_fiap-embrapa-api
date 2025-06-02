from pydantic import BaseModel
from typing import Optional


class ProcessamentoBase(BaseModel):
    cultivar: Optional[str] = None
    quantidade_kg: Optional[float] = None
    tipo: Optional[str] = None
    ano: Optional[str] = None
    categoria: Optional[str] = None
    caracteristica: Optional[str] = None


class ProcessamentoCreate(ProcessamentoBase):
    pass


class ProcessamentoRead(ProcessamentoBase):
    id: int

    class Config:
        orm_mode = True
