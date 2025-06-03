from typing import List, Type
from sqlalchemy.orm import Session
from app.v1.models.predicao_exportacao import PredicaoExportacao
from app.v1.schemas.predicao_exportacao import PredicaoExportacaoCreate


def create_predicao_exportacao(
    db: Session,
    predicao_in: PredicaoExportacaoCreate,
    valor_previsto: float
) -> PredicaoExportacao:
    """
    Insere no banco uma predição de exportação, contendo pais, quantidade_kg, tipo e valor_previsto.
    Retorna o objeto PredicaoExportacao criado.
    """
    obj = PredicaoExportacao(
        pais=predicao_in.pais,
        quantidade_kg=predicao_in.quantidade_kg,
        tipo=predicao_in.tipo,
        valor_previsto=valor_previsto
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_predicoes_exportacao(
    db: Session
) -> list[Type[PredicaoExportacao]]:
    """
    Retorna todas as predições de exportação já salvas no banco,
    ordenadas do mais recente para o mais antigo.
    """
    return db.query(PredicaoExportacao).order_by(PredicaoExportacao.created_at.desc()).all()
