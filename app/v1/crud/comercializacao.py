from typing import List, Optional
from sqlalchemy.orm import Session
from app.v1.models.comercializacao import Comercializacao
from app.v1.schemas.comercializacao import ComercializacaoBase


def create_comercializacoes(
    db: Session,
    registros: List[ComercializacaoBase]
) -> List[Comercializacao]:
    """
    Insere em lote todos os registros de ComercializacaoBase no banco.
    Retorna a lista de objetos Comercializacao (já com id).
    """
    objetos = []
    for item in registros:
        obj = Comercializacao(
            produto=item.produto,
            quantidade_l=item.quantidade_l,
            tipo=item.tipo,
            ano=item.ano,
        )
        db.add(obj)
        objetos.append(obj)

    db.commit()
    for obj in objetos:
        db.refresh(obj)
    return objetos


def create_comercializacao(
    db: Session,
    registro: ComercializacaoBase
) -> Comercializacao:
    """
    Insere um único registro de ComercializacaoBase e retorna o objeto criado.
    """
    obj = Comercializacao(
        produto=registro.produto,
        quantidade_l=registro.quantidade_l,
        tipo=registro.tipo,
        ano=registro.ano,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_comercializacoes(
    db: Session,
    produtos: Optional[List[str]] = None,
    tipos: Optional[List[str]] = None,
    quantidade_minima: Optional[int] = None,
    quantidade_maxima: Optional[int] = None,
    anos: Optional[List[int]] = None,
) -> List[Comercializacao]:
    """
    Retorna todos os registros que atendem aos filtros fornecidos.
    Se um parâmetro for None ou lista vazia, esse filtro é ignorado.
    """
    query = db.query(Comercializacao)

    if produtos:
        query = query.filter(Comercializacao.produto.in_(produtos))
    if tipos:
        query = query.filter(Comercializacao.tipo.in_(tipos))
    if quantidade_minima is not None:
        query = query.filter(Comercializacao.quantidade_l >= quantidade_minima)
    if quantidade_maxima is not None:
        query = query.filter(Comercializacao.quantidade_l <= quantidade_maxima)
    if anos:
        anos_str = [str(a) for a in anos]
        query = query.filter(Comercializacao.ano.in_(anos_str))

    return query.all()
