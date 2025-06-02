from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from typing import List

from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.comercializacao import ComercializacaoOut

router = APIRouter(prefix="/comercializacao", tags=["Comercialização"])

scraper = EmbrapaScraper()


@router.get("", response_model=List[ComercializacaoOut])
async def get_comercializacao(
        ano: List[int] = Query([2023], description="Repita o parâmetro para cada ano")
):
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "url": f"{URL}?opcao=opt_04",
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




