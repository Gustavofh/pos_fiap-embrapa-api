from typing import List, Optional, Type
from sqlalchemy.orm import Session
from app.v1.models.processamento import Processamento
from app.v1.schemas.processamento import ProcessamentoBase


def create_processamentos(
    db: Session,
    registros: List[ProcessamentoBase]
) -> List[Processamento]:
    """
    Insere em lote todos os registros de ProcessamentoBase no banco.
    Retorna a lista de objetos Processamento (já com id).
    """
    objetos = []
    for item in registros:
        obj = Processamento(
            cultivar=item.cultivar,
            quantidade_kg=item.quantidade_kg,
            tipo=item.tipo,
            caracteristica=item.caracteristica,
            ano=item.ano,
        )
        db.add(obj)
        objetos.append(obj)

    db.commit()
    for obj in objetos:
        db.refresh(obj)
    return objetos


def create_processamento(
    db: Session,
    registro: ProcessamentoBase
) -> Processamento:
    """
    Insere um único registro de ProcessamentoBase e retorna o objeto criado.
    """
    obj = Processamento(
        cultivar=registro.cultivar,
        quantidade_kg=registro.quantidade_kg,
        tipo=registro.tipo,
        caracteristica=registro.caracteristica,
        ano=registro.ano,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_processamentos(
    db: Session,
    cultivares: Optional[List[str]] = None,
    tipos: Optional[List[str]] = None,
    caracteristicas: Optional[List[str]] = None,
    quantidade_minima: Optional[int] = None,
    quantidade_maxima: Optional[int] = None,
    anos: Optional[List[int]] = None,
) -> list[Type[Processamento]]:
    """
    Retorna todos os registros que atendem aos filtros fornecidos.
    Se um parâmetro for None ou lista vazia, esse filtro é ignorado.
    """
    query = db.query(Processamento)

    if cultivares:
        query = query.filter(Processamento.cultivar.in_(cultivares))
    if tipos:
        query = query.filter(Processamento.tipo.in_(tipos))
    if caracteristicas:
        query = query.filter(Processamento.caracteristica.in_(caracteristicas))
    if quantidade_minima is not None:
        query = query.filter(Processamento.quantidade_kg >= quantidade_minima)
    if quantidade_maxima is not None:
        query = query.filter(Processamento.quantidade_kg <= quantidade_maxima)
    if anos:
        anos_str = [str(a) for a in anos]
        query = query.filter(Processamento.ano.in_(anos_str))

    return query.all()
