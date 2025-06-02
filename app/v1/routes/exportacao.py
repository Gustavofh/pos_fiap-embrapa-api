from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from typing import List

from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.exportacao import ExportacaoOut

router = APIRouter(prefix="/exportacao", tags=["Exportacao"])

scraper = EmbrapaScraper()


@router.get("", response_model=List[ExportacaoOut])
async def get_processamento(
        ano: List[int] = Query(list(range(1970, 2025)), description="Repita o parâmetro para cada ano")
):
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "main_cols": "paises",
        "numeric_cols": ['quantidade_kg', "valor_dolar"]
    }
    types = {
        "vinhos_de_mesa": f'{URL}?opcao=opt_06&subopcao=subopt_01',
        "espumantes": f'{URL}?opcao=opt_06&subopcao=subopt_02',
        "uvas_frescas": f'{URL}?opcao=opt_06&subopcao=subopt_03',
        "suco_de_uva": f'{URL}?opcao=opt_06&subopcao=subopt_04',
    }

    scraper = EmbrapaScraper()
    df = pd.DataFrame(columns=['paises', 'quantidade_kg', 'valor_dolar', 'tipo', 'ano'])
    for tipo, url in types.items():
        print(url)
        df_aux = create_dataframe(
            scraper=scraper,
            url=url,
            main_cols=config["main_cols"],
            numeric_cols=config["numeric_cols"],
            anos=ano,
            tipo=tipo
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
