import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.v1.models.processamento import Processamento
from app.v1.schemas.processamento import ProcessamentoCreate, ProcessamentoRead
from app.v1.crud.processamento import create_processamento
from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper

router = APIRouter(prefix="/processamento", tags=["Processamento"])


# @router.get("/", response_model=List[ProcessamentoRead])
# async def list_producao(
#     ano: Optional[str] = Query(None),
#     tipo: Optional[str] = Query(None),
#     min_quantidade: Optional[float] = Query(None, alias="minQuantidade"),
#     max_quantidade: Optional[float] = Query(None, alias="maxQuantidade"),
#     cultivar: Optional[str] = Query(None),
#     categoria: Optional[str] = Query(None),
#     caracteristica: Optional[str] = Query(None),
#     db: AsyncSession = Depends(get_db),
# ):
#     return await get_producoes(
#         db,
#         ano=ano,
#         tipo=tipo,
#         min_quantidade=min_quantidade,
#         max_quantidade=max_quantidade,
#         cultivar=cultivar,
#         categoria=categoria,
#         caracteristica=caracteristica,
#     )

@router.get("/update")
async def update_processamento(db: AsyncSession = Depends(get_db)):
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"

    config = {
        "main_cols": "cultivar",
        "numeric_cols": ['quantidade_kg']
    }

    types = {
        "vinifera": f'{URL}?opcao=opt_03&subopcao=subopt_01',
        "americanas_e_hibridas": f'{URL}?opcao=opt_03&subopcao=subopt_02',
        "uvas_de_mesa": f'{URL}?opcao=opt_03&subopcao=subopt_03',
    }

    scraper = EmbrapaScraper()
    df_final = pd.DataFrame(columns=['cultivar', 'quantidade_kg', 'tipo', 'caracteristica', 'ano'])
    for tipo, url in types.items():
        df = create_dataframe(scraper, url=url, main_cols=config.get("main_cols"),
                              numeric_cols=config.get("numeric_cols"), ano=1970, tipo=tipo, caracteristica=True)

        df_final = pd.concat([df_final, df], ignore_index=True)
    df_final = (
        df_final.replace({np.nan: None, "": None})
        .assign(
            quantidade_kg=lambda d: pd.to_numeric(
                d.quantidade_kg, errors="coerce"
            )
        )
        .replace({np.nan: None})
    )

    rows = df_final.to_dict(orient="records")
    if rows:
        await db.execute(insert(Processamento), rows)
        await db.commit()

    return {"message": f"{len(rows)} registros inseridos com sucesso."}
