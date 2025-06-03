from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.v1.crud.exportacao import (
    create_exportacoes,
    get_exportacoes as crud_get_exportacoes,
    create_exportacao as crud_create_exportacao
)
from app.core.database import get_db
from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.exportacao import ExportacaoBase, ExportacaoOut

router = APIRouter(prefix="/exportacao", tags=["Exportacao"])
scraper = EmbrapaScraper()


@router.get(
    "/update",
    response_model=List[ExportacaoOut],
    status_code=status.HTTP_201_CREATED
)
def update_exportacao(
    db: Session = Depends(get_db),
    ano: List[int] = Query(
        list(range(1970, 2025)), description="Repita o parâmetro para cada ano"
    )
):
    """
    GET /exportacao/update:
    - Faz scraping de TODOS os anos (default 1970–2024) e salva tudo no banco (sem filtros).
    - Retorna a lista de objetos ExportacaoOut criados.
    """
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "main_cols": "paises",
        "numeric_cols": ["quantidade_kg", "valor_dolar"]
    }
    types = {
        "vinhos_de_mesa": f"{URL}?opcao=opt_06&subopcao=subopt_01",
        "espumantes": f"{URL}?opcao=opt_06&subopcao=subopt_02",
        "uvas_frescas": f"{URL}?opcao=opt_06&subopcao=subopt_03",
        "suco_de_uva": f"{URL}?opcao=opt_06&subopcao=subopt_04",
    }

    df = pd.DataFrame(columns=["paises", "quantidade_kg", "valor_dolar", "tipo", "ano"])
    for tipo_key, url in types.items():
        df_aux = create_dataframe(
            scraper=scraper,
            url=url,
            main_cols=config["main_cols"],
            numeric_cols=config["numeric_cols"],
            anos=ano,
            tipo=tipo_key
        )
        df = pd.concat([df, df_aux], ignore_index=True)

    if df.empty:
        anos_str = ", ".join(map(str, ano))
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum dado encontrado para o(s) ano(s): {anos_str}"
        )

    registros: List[ExportacaoBase] = []
    for row in df.to_dict(orient="records"):
        item = ExportacaoBase(
            paises=row["paises"],
            quantidade_kg=int(row["quantidade_kg"]),
            valor_dolar=int(row["valor_dolar"]),
            tipo=row["tipo"],
            ano=str(row["ano"])
        )
        registros.append(item)

    criados = create_exportacoes(db=db, registros=registros)
    return criados


@router.get(
    "",
    response_model=List[ExportacaoOut]
)
def read_exportacoes(
    pais: Optional[List[str]] = Query([], description="País(es) para filtrar"),
    tipo: Optional[List[str]] = Query([], description="Tipo(s) para filtrar"),
    quantidadeMinima: Optional[int] = Query(None, description="Quantidade mínima"),
    quantidadeMaxima: Optional[int] = Query(None, description="Quantidade máxima"),
    valorMinimo: Optional[int] = Query(None, description="Valor mínimo em dólar"),
    valorMaximo: Optional[int] = Query(None, description="Valor máximo em dólar"),
    ano: Optional[List[int]] = Query([], description="Ano(s) para filtrar"),
    db: Session = Depends(get_db),
):
    """
    GET /exportacao:
    - Lê do banco todos os registros de exportação.
    - Aplica filtros via query params (pais, tipo, quantidade e valor e ano).
    """
    filtros_anos = ano if ano else None

    registros = crud_get_exportacoes(
        db=db,
        paises=pais or None,
        tipos=tipo or None,
        quantidade_minima=quantidadeMinima,
        quantidade_maxima=quantidadeMaxima,
        valor_minimo=valorMinimo,
        valor_maximo=valorMaximo,
        anos=filtros_anos
    )
    return registros


@router.post(
    "",
    response_model=ExportacaoOut,
    status_code=status.HTTP_201_CREATED
)
def create_exportacao_manual(
    registro: ExportacaoBase,
    db: Session = Depends(get_db)
):
    """
    POST /exportacao:
    - Recebe manualmente (JSON) um registro ExportacaoBase e insere no banco.
    - Retorna o registro criado (com id).
    """
    criado = crud_create_exportacao(db=db, registro=registro)
    return criado
