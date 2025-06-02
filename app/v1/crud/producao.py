from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.models.producao import Producao
from app.v1.schemas.producao import ProducaoCreate


async def get_producoes(
    db: AsyncSession,
    ano: Optional[str] = None,
    tipo: Optional[str] = None,
    min_quantidade: Optional[float] = None,
    max_quantidade: Optional[float] = None,
    cultivar: Optional[str] = None,
    categoria: Optional[str] = None,
    caracteristica: Optional[str] = None,
) -> List[Producao]:
    q = select(Producao)
    conds = []

    if ano:
        conds.append(Producao.ano == ano)
    if tipo:
        conds.append(Producao.tipo == tipo)
    if min_quantidade is not None:
        conds.append(Producao.quantidade_kg >= min_quantidade)
    if max_quantidade is not None:
        conds.append(Producao.quantidade_kg <= max_quantidade)
    if cultivar:
        conds.append(Producao.cultivar == cultivar)
    if categoria:
        conds.append(Producao.categoria == categoria)
    if caracteristica:
        conds.append(Producao.caracteristica == caracteristica)

    if conds:
        q = q.where(and_(*conds))

    res = await db.execute(q)
    return res.scalars().all()


async def get_producao_by_id(db: AsyncSession, producao_id: int) -> Optional[Producao]:
    res = await db.execute(select(Producao).where(Producao.id == producao_id))
    return res.scalars().first()


async def create_producao(db: AsyncSession, producao_in: ProducaoCreate) -> Producao:
    """
    Mantida apenas para inserções unitárias; usa flush em vez de commit.
    """
    producao = Producao(**producao_in.dict())
    db.add(producao)
    await db.flush()   # guarda na transação aberta
    await db.refresh(producao)
    return producao
