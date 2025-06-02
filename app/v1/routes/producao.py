from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from typing import List

from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper

router = APIRouter(prefix="/producao", tags=["Produção"])

scraper = EmbrapaScraper()


@router.get("")
async def get_producao(
        ano: List[int] = Query(..., description="Repita o parâmetro para cada ano")
):
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "url": f"{URL}?opcao=opt_02",
        "main_cols": "produto",
        "numeric_cols": ["quantidade_l"],
    }
    scraper = EmbrapaScraper()
    df = create_dataframe(
        scraper=scraper,
        url=config["url"],
        main_cols=config["main_cols"],
        numeric_cols=config["numeric_cols"],
        anos=ano
    )
    if df.empty:
        anos_str = ", ".join(map(str, ano))
        raise HTTPException(404, f"Nenhum dado encontrado para o(s) ano(s): {anos_str}")

    rows = (
        df.where(pd.notnull(df), None)
          .to_dict(orient="records")
    )
    return rows




