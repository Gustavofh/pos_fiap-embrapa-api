from pydantic import BaseModel


class ComercializacaoBase(BaseModel):
    produto: str
    quantidade_l: int
    tipo: str
    ano: str


class ComercializacaoOut(ComercializacaoBase):
    id: int

    class Config:
        orm_mode = True
