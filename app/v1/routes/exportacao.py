from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from typing import List

from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.exportacao import ExportacaoOut

router = APIRouter(prefix="/exportacao", tags=["Exportacao"])

scraper = EmbrapaScraper()


@router.get("", response_model=List[ExportacaoOut])
async def get_exportacao(
        pais: List[str] = Query([], description="Paises(s) a ser coletado"),
        tipo: List[str] = Query([], description="Tipo(s) a ser coletado"),
        quantidadeMinima: int = Query(None, description="Quantidade mínima a ser coletada"),
        quantidadeMaxima: int = Query(None, description="Quantidade máxima a ser coletada"),
        valorMinimo: int = Query(None, description="Quantidade mínima a ser coletada"),
        valorMaximo: int = Query(None, description="Quantidade máxima a ser coletada"),
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
    for type, url in types.items():
        df_aux = create_dataframe(
            scraper=scraper,
            url=url,
            main_cols=config["main_cols"],
            numeric_cols=config["numeric_cols"],
            anos=ano,
            tipo=type
        )
        df = pd.concat([df, df_aux], ignore_index=True)

    if df.empty:
        anos_str = ", ".join(map(str, ano))
        raise HTTPException(404, f"Nenhum dado encontrado para o(s) ano(s): {anos_str}")

    if pais:
        df = df[df["paises"].isin(pais)]
    if tipo:
        df = df[df["tipo"].isin(tipo)]
    if quantidadeMinima:
        df = df.loc[df["quantidade_kg"] >= quantidadeMinima]
    if quantidadeMaxima:
        df = df[df["quantidade_kg"] <= quantidadeMaxima]
    if valorMinimo:
        df = df.loc[df["valor_dolar"] >= valorMinimo]
    if valorMaximo:
        df = df[df["valor_dolar"] <= valorMaximo]

    rows = (
        df.where(pd.notnull(df), None)
          .to_dict(orient="records")
    )
    return rows
