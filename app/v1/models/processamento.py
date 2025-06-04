from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Processamento(Base):
    __tablename__ = "processamento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cultivar = Column(String, nullable=False)
    quantidade_kg = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    caracteristica = Column(String, nullable=False)
    ano = Column(String, nullable=False)
