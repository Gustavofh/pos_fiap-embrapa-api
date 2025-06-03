from pydantic import BaseModel


class PredicaoExportacaoBase(BaseModel):
    pais: str
    quantidade_kg: int
    tipo: str


class PredicaoExportacaoCreate(PredicaoExportacaoBase):
    pass


class PredicaoExportacaoOut(PredicaoExportacaoBase):
    id: int
    valor_previsto: float
    created_at: str

    class Config:
        orm_mode = True
