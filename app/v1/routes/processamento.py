from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from typing import List

from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper

router = APIRouter(prefix="/processamento", tags=["Processamento"])

scraper = EmbrapaScraper()


@router.get("")
async def get_processamento(
        ano: List[int] = Query(2023, description="Repita o parâmetro para cada ano")
):
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
    df = pd.DataFrame(columns=['cultivar', 'quantidade_kg', 'tipo', 'caracteristica', 'ano'])
    for tipo, url in types.items():
        print(url)
        df_aux = create_dataframe(
            scraper=scraper,
            url=url,
            main_cols=config["main_cols"],
            numeric_cols=config["numeric_cols"],
            anos=ano,
            tipo=tipo,
            caracteristica=True
        )
        df = pd.concat([df, df_aux], ignore_index=True)

    if df.empty:
        anos_str = ", ".join(map(str, ano))
        raise HTTPException(404, f"Nenhum dado encontrado para o(s) ano(s): {anos_str}")

    rows = (
        df.where(pd.notnull(df), None)
          .to_dict(orient="records")
    )
    return rows
