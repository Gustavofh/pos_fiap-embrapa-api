from pydantic import BaseModel


class ProcessamentoBase(BaseModel):
    cultivar: str
    quantidade_kg: int
    tipo: str
    caracteristica: str
    ano: str


class ProcessamentoOut(ProcessamentoBase):
    id: int

    class Config:
        orm_mode = True
