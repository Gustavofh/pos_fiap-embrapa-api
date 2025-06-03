from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.core.database import Base


class PredicaoExportacao(Base):
    __tablename__ = "predicao_exportacao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pais = Column(String, nullable=False)
    quantidade_kg = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    valor_previsto = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )
