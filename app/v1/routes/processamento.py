from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.v1.crud.processamento import (
    create_processamentos,
    get_processamentos as crud_get_processamentos,
    create_processamento as crud_create_processamento
)
from app.core.database import get_db
from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.processamento import ProcessamentoBase, ProcessamentoOut

router = APIRouter(prefix="/processamento", tags=["Processamento"])
scraper = EmbrapaScraper()


@router.get(
    "/update",
    response_model=List[ProcessamentoOut],
    status_code=status.HTTP_201_CREATED
)
def update_processamento(
    db: Session = Depends(get_db),
    ano: List[int] = Query(
        list(range(1970, 2025)),
        description="Repita o parâmetro para cada ano"
    )
):
    """
    /processamento/update:
    - Faz scraping de TODOS os anos (default 1970–2024) e salva tudo no banco (sem filtros).
    - Retorna a lista de objetos ProcessamentoOut criados.
    """
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "main_cols": "cultivar",
        "numeric_cols": ["quantidade_kg"]
    }
    types = {
        "vinifera": f"{URL}?opcao=opt_03&subopcao=subopt_01",
        "americanas_e_hibridas": f"{URL}?opcao=opt_03&subopcao=subopt_02",
        "uvas_de_mesa": f"{URL}?opcao=opt_03&subopcao=subopt_03",
    }

    df = pd.DataFrame(columns=["cultivar", "quantidade_kg", "tipo", "caracteristica", "ano"])
    for tipo_key, url in types.items():
        df_aux = create_dataframe(
            scraper=scraper,
            url=url,
            main_cols=config["main_cols"],
            numeric_cols=config["numeric_cols"],
            anos=ano,
            tipo=tipo_key,
            caracteristica=True
        )
        df = pd.concat([df, df_aux], ignore_index=True)

    if df.empty:
        anos_str = ", ".join(map(str, ano))
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum dado encontrado para o(s) ano(s): {anos_str}"
        )

    registros: List[ProcessamentoBase] = []
    for row in df.to_dict(orient="records"):
        item = ProcessamentoBase(
            cultivar=row["cultivar"],
            quantidade_kg=int(row["quantidade_kg"]),
            tipo=row["tipo"],
            caracteristica=row["caracteristica"],
            ano=str(row["ano"])
        )
        registros.append(item)

    dados = create_processamentos(db=db, registros=registros)
    return dados


@router.get(
    "",
    response_model=List[ProcessamentoOut],
    status_code=status.HTTP_200_OK
)
def read_processamentos(
    cultivar: Optional[List[str]] = Query([], description="Cultivar(es) para filtrar"),
    tipo: Optional[List[str]] = Query([], description="Tipo(s) para filtrar"),
    caracteristica: Optional[List[str]] = Query([], description="Característica(s) para filtrar"),
    quantidadeMinima: Optional[int] = Query(None, description="Quantidade mínima"),
    quantidadeMaxima: Optional[int] = Query(None, description="Quantidade máxima"),
    ano: Optional[List[int]] = Query([], description="Ano(s) para filtrar"),
    db: Session = Depends(get_db),
):
    """
    GET /processamento:
    - Lê do banco todos os registros de processamento.
    - Aplica os filtros via query params (cultivar, tipo, caracteristica, quantidade e ano).
    """
    filtros_anos = ano if ano else None

    dados = crud_get_processamentos(
        db=db,
        cultivares=cultivar or None,
        tipos=tipo or None,
        caracteristicas=caracteristica or None,
        quantidade_minima=quantidadeMinima,
        quantidade_maxima=quantidadeMaxima,
        anos=filtros_anos
    )
    if len(dados) != 0:
        return dados
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Registros não encontrados. Altere os parametros de filtro."
    )


@router.post(
    "",
    response_model=ProcessamentoOut,
    status_code=status.HTTP_201_CREATED
)
def create_processamento_manual(
    registro: ProcessamentoBase,
    db: Session = Depends(get_db)
):
    """
    POST /processamento:
    - Recebe manualmente (JSON) um registro ProcessamentoBase e insere no banco.
    - Retorna o registro criado (com id).
    """
    dados = crud_create_processamento(db=db, registro=registro)
    return dados
