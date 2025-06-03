from typing import List, Type
from sqlalchemy.orm import Session
from app.v1.models.predicao_producao import PredicaoProducao
from app.v1.schemas.predicao_producao import PredicaoProducaoCreate


def create_predicao_producao(
    db: Session,
    predicao_in: PredicaoProducaoCreate,
    valor_previsto: float
) -> PredicaoProducao:
    """
    Insere no banco uma predição de produção, contendo produto, tipo, ano e valor_previsto.
    Retorna o objeto PredicaoProducao criado.
    """
    obj = PredicaoProducao(
        produto=predicao_in.produto,
        tipo=predicao_in.tipo,
        ano=predicao_in.ano,
        valor_previsto=valor_previsto
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_predicoes_producao(
    db: Session
) -> list[Type[PredicaoProducao]]:
    """
    Retorna todas as predições de produção já salvas no banco,
    ordenadas do mais recente para o mais antigo.
    """
    return db.query(PredicaoProducao).order_by(PredicaoProducao.created_at.desc()).all()
