from pydantic import BaseModel


class ExportacaoBase(BaseModel):
    paises: str
    quantidade_kg: int
    valor_dolar: int
    tipo: str
    ano: str


class ExportacaoOut(ExportacaoBase):
    id: int

    class Config:
        orm_mode = True
