from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.v1.crud.comercializacao import (
    create_comercializacoes,
    get_comercializacoes as crud_get_comercializacoes,
    create_comercializacao as crud_create_comercializacao
)
from app.core.database import get_db
from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.comercializacao import ComercializacaoBase, ComercializacaoOut

router = APIRouter(prefix="/comercializacao", tags=["Comercialização"])
scraper = EmbrapaScraper()


@router.get(
    "/update",
    response_model=List[ComercializacaoOut],
    status_code=status.HTTP_201_CREATED
)
def update_comercializacao(
    db: Session = Depends(get_db),
    ano: List[int] = Query(
        list(range(1970, 2025)), description="Repita o parâmetro para cada ano"
    )
):
    """
    /comercializacao/update:
    - Faz scraping de TODOS os anos (default 1970–2024) e salva tudo no banco (sem filtros).
    - Retorna a lista de objetos ComercializacaoOut criados.
    """
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "url": f"{URL}?opcao=opt_04",
        "main_cols": "produto",
        "numeric_cols": ["quantidade_l"]
    }

    df = create_dataframe(
        scraper=scraper,
        url=config["url"],
        main_cols=config["main_cols"],
        numeric_cols=config["numeric_cols"],
        anos=ano
    )

    if df.empty:
        anos_str = ", ".join(map(str, ano))
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum dado encontrado para o(s) ano(s): {anos_str}"
        )

    registros: List[ComercializacaoBase] = []
    for row in df.to_dict(orient="records"):
        item = ComercializacaoBase(
            produto=row["produto"],
            quantidade_l=int(row["quantidade_l"]),
            tipo=row["tipo"],
            ano=str(row["ano"])
        )
        registros.append(item)

    criados = create_comercializacoes(db=db, registros=registros)
    return criados


@router.get(
    "",
    response_model=List[ComercializacaoOut]
)
def read_comercializacoes(
    produto: Optional[List[str]] = Query([], description="Produto(s) para filtrar"),
    tipo: Optional[List[str]] = Query([], description="Tipo(s) para filtrar"),
    quantidadeMinima: Optional[int] = Query(None, description="Quantidade mínima"),
    quantidadeMaxima: Optional[int] = Query(None, description="Quantidade máxima"),
    ano: Optional[List[int]] = Query([], description="Ano(s) para filtrar"),
    db: Session = Depends(get_db),
):
    """
    GET /comercializacao:
    - Lê do banco todos os registros de comercialização.
    - Aplica os filtros via query params (produto, tipo, quantidade e ano).
    """
    filtros_anos = ano if ano else None

    registros = crud_get_comercializacoes(
        db=db,
        produtos=produto or None,
        tipos=tipo or None,
        quantidade_minima=quantidadeMinima,
        quantidade_maxima=quantidadeMaxima,
        anos=filtros_anos
    )
    return registros


@router.post(
    "",
    response_model=ComercializacaoOut,
    status_code=status.HTTP_201_CREATED
)
def create_comercializacao_manual(
    registro: ComercializacaoBase,
    db: Session = Depends(get_db)
):
    """
    POST /comercializacao:
    - Recebe manualmente (JSON) um registro ComercializacaoBase e insere no banco.
    - Retorna o registro criado (com id).
    """
    criado = crud_create_comercializacao(db=db, registro=registro)
    return criado
