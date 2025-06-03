from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.v1.models.importacao import Importacao
from app.v1.schemas.importacao import ImportacaoBase


def create_importacoes(
    db: Session,
    importacoes: List[ImportacaoBase]
) -> List[Importacao]:
    """
    Recebe uma lista de ImportacaoBase (Pydantic) e insere todas no banco.
    Retorna a lista de objetos Importacao inseridos (com id preenchido).
    """
    objetos = []
    for item in importacoes:
        obj = Importacao(
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


def create_importacao(
    db: Session,
    importacao: ImportacaoBase
) -> Importacao:
    """
    Insere apenas um registro no banco e retorna o objeto criado.
    """
    obj = Importacao(
        paises=importacao.paises,
        quantidade_kg=importacao.quantidade_kg,
        valor_dolar=importacao.valor_dolar,
        tipo=importacao.tipo,
        ano=importacao.ano,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_importacoes(
    db: Session,
    paises: Optional[List[str]] = None,
    tipos: Optional[List[str]] = None,
    quantidade_minima: Optional[int] = None,
    quantidade_maxima: Optional[int] = None,
    valor_minimo: Optional[int] = None,
    valor_maximo: Optional[int] = None,
    anos: Optional[List[int]] = None,
) -> List[Importacao]:
    """
    Retorna todos os registros que atendem aos filtros fornecidos.
    Se um parâmetro for None ou lista vazia, ignora esse filtro.
    """

    query = db.query(Importacao)
    if paises:
        query = query.filter(Importacao.paises.in_(paises))
    if tipos:
        query = query.filter(Importacao.tipo.in_(tipos))
    if quantidade_minima is not None:
        query = query.filter(Importacao.quantidade_kg >= quantidade_minima)
    if quantidade_maxima is not None:
        query = query.filter(Importacao.quantidade_kg <= quantidade_maxima)
    if valor_minimo is not None:
        query = query.filter(Importacao.valor_dolar >= valor_minimo)
    if valor_maximo is not None:
        query = query.filter(Importacao.valor_dolar <= valor_maximo)
    if anos:
        anos_str = [str(a) for a in anos]
        query = query.filter(Importacao.ano.in_(anos_str))

    resultados = query.all()
    return resultados
