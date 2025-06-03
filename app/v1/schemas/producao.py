from pydantic import BaseModel


class ProducaoBase(BaseModel):
    produto: str
    quantidade_l: int
    tipo: str
    ano: str


class ProducaoOut(ProducaoBase):
    id: int

    class Config:
        orm_mode = True
