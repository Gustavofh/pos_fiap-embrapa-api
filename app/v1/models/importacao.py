from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Importacao(Base):
    __tablename__ = "importacao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paises = Column(String, nullable=False)
    quantidade_kg = Column(Integer, nullable=False)
    valor_dolar = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    ano = Column(String, nullable=False)
