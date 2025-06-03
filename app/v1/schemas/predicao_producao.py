from pydantic import BaseModel


class PredicaoProducaoBase(BaseModel):
    produto: str
    tipo: str
    ano: str


class PredicaoProducaoCreate(PredicaoProducaoBase):
    pass


class PredicaoProducaoOut(PredicaoProducaoBase):
    id: int
    valor_previsto: float
    created_at: str

    class Config:
        orm_mode = True
