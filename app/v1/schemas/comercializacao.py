from pydantic import BaseModel


class ComercializacaoBase(BaseModel):
    cultivar: str
    quantidade_kg: int
    tipo: str
    caracteristica: str
    ano: str


class ComercializacaoOut(ComercializacaoBase):
    pass


