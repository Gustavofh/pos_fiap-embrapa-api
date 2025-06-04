from pydantic import BaseModel


class ImportacaoBase(BaseModel):
    paises: str
    quantidade_kg: int
    valor_dolar: int
    tipo: str
    ano: str


class ImportacaoOut(ImportacaoBase):
    pass

