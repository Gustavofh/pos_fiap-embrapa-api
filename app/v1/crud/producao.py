from typing import List, Optional, Type
from sqlalchemy.orm import Session
from app.v1.models.producao import Producao
from app.v1.schemas.producao import ProducaoBase


def create_producoes(
    db: Session,
    registros: List[ProducaoBase]
) -> List[Producao]:
    """
    Insere em lote todos os registros de ProducaoBase no banco.
    Retorna a lista de objetos Producao (já com id).
    """
    objetos = []
    for item in registros:
        obj = Producao(
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


def create_producao(
    db: Session,
    registro: ProducaoBase
) -> Producao:
    """
    Insere um único registro de ProducaoBase e retorna o objeto criado.
    """
    obj = Producao(
        produto=registro.produto,
        quantidade_l=registro.quantidade_l,
        tipo=registro.tipo,
        ano=registro.ano,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_producoes(
    db: Session,
    produtos: Optional[List[str]] = None,
    tipos: Optional[List[str]] = None,
    quantidade_minima: Optional[int] = None,
    quantidade_maxima: Optional[int] = None,
    anos: Optional[List[int]] = None,
) -> list[Type[Producao]]:
    """
    Retorna todos os registros que atendem aos filtros fornecidos.
    Se um parâmetro for None ou lista vazia, esse filtro é ignorado.
    """
    query = db.query(Producao)

    if produtos:
        query = query.filter(Producao.produto.in_(produtos))
    if tipos:
        query = query.filter(Producao.tipo.in_(tipos))
    if quantidade_minima is not None:
        query = query.filter(Producao.quantidade_l >= quantidade_minima)
    if quantidade_maxima is not None:
        query = query.filter(Producao.quantidade_l <= quantidade_maxima)
    if anos:
        anos_str = [str(a) for a in anos]
        query = query.filter(Producao.ano.in_(anos_str))

    return query.all()
