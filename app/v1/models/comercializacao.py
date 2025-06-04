from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Comercializacao(Base):
    __tablename__ = "comercializacao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    produto = Column(String, nullable=False)
    quantidade_l = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    ano = Column(String, nullable=False)
