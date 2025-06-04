from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.core.database import Base


class PredicaoProducao(Base):
    __tablename__ = "predicao_producao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    produto = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    ano = Column(String, nullable=False)
    valor_previsto = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )
