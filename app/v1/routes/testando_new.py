from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from typing import List

from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper

router = APIRouter(prefix="/teste", tags=["Teste"])

scraper = EmbrapaScraper()


@router.get("")
async def testando(
        ano: List[int] = Query(..., description="Repita o parâmetro para cada ano")
):
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "url": f"{URL}?opcao=opt_02",
        "main_cols": "produto",
        "numeric_cols": ["quantidade_l"],
    }

    scraper = EmbrapaScraper()
    df = create_dataframe(scraper, url=config["url"], main_cols=config["main_cols"],
                          numeric_cols=config["numeric_cols"], anos=ano)
    rows = (
        df.where(pd.notnull(df), None)                # ou df.replace({np.nan: None})
          .to_dict(orient="records")
    )
    return rows



