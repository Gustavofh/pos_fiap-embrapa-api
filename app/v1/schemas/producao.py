from pydantic import BaseModel
from typing import Optional


class ProducaoBase(BaseModel):
    cultivar: Optional[str] = None
    quantidade_l: Optional[float] = None
    tipo: Optional[str] = None
    ano: Optional[str] = None
    categoria: Optional[str] = None
    caracteristica: Optional[str] = None


class ProducaoCreate(ProducaoBase):
    pass


class ProducaoRead(ProducaoBase):
    id: int

    class Config:
        orm_mode = True
