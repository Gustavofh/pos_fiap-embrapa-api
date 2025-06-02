from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Processamento(Base):
    __tablename__ = "processamento"

    id = Column(Integer, primary_key=True, index=True)
    cultivar = Column(String, nullable=True)
    quantidade_kg = Column(Float, nullable=True)
    tipo = Column(String, nullable=True)
    ano = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    caracteristica = Column(String, nullable=True)
