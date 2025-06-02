import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.v1.models.producao import Producao
from app.v1.schemas.producao import ProducaoCreate, ProducaoRead
from app.v1.crud.producao import get_producoes, get_producao_by_id
from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper

router = APIRouter(prefix="/producao", tags=["Produção"])


@router.get("/", response_model=List[ProducaoRead])
async def list_producao(
    ano: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    min_quantidade: Optional[float] = Query(None, alias="minQuantidade"),
    max_quantidade: Optional[float] = Query(None, alias="maxQuantidade"),
    cultivar: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    caracteristica: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_producoes(
        db,
        ano=ano,
        tipo=tipo,
        min_quantidade=min_quantidade,
        max_quantidade=max_quantidade,
        cultivar=cultivar,
        categoria=categoria,
        caracteristica=caracteristica,
    )


@router.get("/update")
async def update_producao(db: AsyncSession = Depends(get_db)):
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "url": f"{URL}?opcao=opt_02",
        "main_cols": "produto",
        "numeric_cols": ["quantidade_l"],
    }

    scraper = EmbrapaScraper()
    df = create_dataframe(scraper, url=config["url"], main_cols=config["main_cols"],
                          numeric_cols=config["numeric_cols"], ano=1970).rename(
        columns={"produto": "cultivar"}
    )

    df = df.replace({np.nan: None, "": None})
    df["quantidade_l"] = pd.to_numeric(df["quantidade_l"], errors="coerce")
    df = df.replace({np.nan: None})

    rows = df.to_dict(orient="records")
    if rows:
        await db.execute(insert(Producao), rows)
        await db.commit()

    return {"message": f"{len(rows)} registros inseridos com sucesso."}
