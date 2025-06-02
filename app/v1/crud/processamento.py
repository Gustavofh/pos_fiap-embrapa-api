from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.models.processamento import Processamento
from app.v1.schemas.processamento import ProcessamentoCreate


async def get_producoes(
    db: AsyncSession,
    ano: Optional[str] = None,
    tipo: Optional[str] = None,
    min_quantidade: Optional[float] = None,
    max_quantidade: Optional[float] = None,
    cultivar: Optional[str] = None,
    categoria: Optional[str] = None,
    caracteristica: Optional[str] = None,
) -> List[Processamento]:
    q = select(Processamento)
    conds = []

    if ano:
        conds.append(Processamento.ano == ano)
    if tipo:
        conds.append(Processamento.tipo == tipo)
    if min_quantidade is not None:
        conds.append(Processamento.quantidade_kg >= min_quantidade)
    if max_quantidade is not None:
        conds.append(Processamento.quantidade_kg <= max_quantidade)
    if cultivar:
        conds.append(Processamento.cultivar == cultivar)
    if categoria:
        conds.append(Processamento.categoria == categoria)
    if caracteristica:
        conds.append(Processamento.caracteristica == caracteristica)

    if conds:
        q = q.where(and_(*conds))

    res = await db.execute(q)
    return res.scalars().all()

async def create_processamento(db: AsyncSession, processamento_in: ProcessamentoCreate) -> Processamento:
    """
    Mantida apenas para inserções unitárias; usa flush em vez de commit.
    """
    processamento = Processamento(**processamento_in.dict())
    db.add(processamento)
    await db.flush()
    await db.refresh(processamento)
    return processamento
