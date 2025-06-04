from typing import List, Optional, Type
from sqlalchemy.orm import Session
from app.v1.models.exportacao import Exportacao
from app.v1.schemas.exportacao import ExportacaoBase


def create_exportacoes(
    db: Session,
    registros: List[ExportacaoBase]
) -> List[Exportacao]:
    """
    Insere em lote todos os registros de ExportacaoBase no banco.
    Retorna a lista de objetos Exportacao (já com id).
    """
    objetos = []
    for item in registros:
        obj = Exportacao(
            paises=item.paises,
            quantidade_kg=item.quantidade_kg,
            valor_dolar=item.valor_dolar,
            tipo=item.tipo,
            ano=item.ano,
        )
        db.add(obj)
        objetos.append(obj)

    db.commit()
    for obj in objetos:
        db.refresh(obj)
    return objetos


def create_exportacao(
    db: Session,
    registro: ExportacaoBase
) -> Exportacao:
    """
    Insere um único registro de ExportacaoBase e retorna o objeto criado.
    """
    obj = Exportacao(
        paises=registro.paises,
        quantidade_kg=registro.quantidade_kg,
        valor_dolar=registro.valor_dolar,
        tipo=registro.tipo,
        ano=registro.ano,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_exportacoes(
    db: Session,
    paises: Optional[List[str]] = None,
    tipos: Optional[List[str]] = None,
    quantidade_minima: Optional[int] = None,
    quantidade_maxima: Optional[int] = None,
    valor_minimo: Optional[int] = None,
    valor_maximo: Optional[int] = None,
    anos: Optional[List[int]] = None,
) -> list[Type[Exportacao]]:
    """
    Retorna todos os registros que atendem aos filtros fornecidos.
    Se um parâmetro for None ou lista vazia, esse filtro é ignorado.
    """
    query = db.query(Exportacao)

    if paises:
        query = query.filter(Exportacao.paises.in_(paises))
    if tipos:
        query = query.filter(Exportacao.tipo.in_(tipos))
    if quantidade_minima is not None:
        query = query.filter(Exportacao.quantidade_kg >= quantidade_minima)
    if quantidade_maxima is not None:
        query = query.filter(Exportacao.quantidade_kg <= quantidade_maxima)
    if valor_minimo is not None:
        query = query.filter(Exportacao.valor_dolar >= valor_minimo)
    if valor_maximo is not None:
        query = query.filter(Exportacao.valor_dolar <= valor_maximo)
    if anos:
        anos_str = [str(a) for a in anos]
        query = query.filter(Exportacao.ano.in_(anos_str))

    return query.all()
