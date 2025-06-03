# app/v1/routes/producao.py
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.v1.crud.producao import (
    create_producoes,
    get_producoes as crud_get_producoes,
    create_producao as crud_create_producao
)
from app.core.database import get_db
from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.producao import ProducaoBase, ProducaoOut

router = APIRouter(prefix="/producao", tags=["Produção"])
scraper = EmbrapaScraper()


@router.get(
    "/update",
    response_model=List[ProducaoOut],
    status_code=status.HTTP_201_CREATED
)
def update_producao(
    db: Session = Depends(get_db),
    ano: List[int] = Query(
        list(range(1970, 2025)), description="Repita o parâmetro para cada ano"
    )
):
    """
    /producao/update:
    - Faz scraping de TODOS os anos (default 1970–2024) e salva tudo no banco (sem filtros).
    - Retorna a lista de objetos ProducaoOut criados.
    """
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "url": f"{URL}?opcao=opt_02",
        "main_cols": "produto",
        "numeric_cols": ["quantidade_l"],
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

    registros: List[ProducaoBase] = []
    for row in df.to_dict(orient="records"):
        item = ProducaoBase(
            produto=row["produto"],
            quantidade_l=int(row["quantidade_l"]),
            tipo=row["tipo"],
            ano=str(row["ano"])
        )
        registros.append(item)

    criados = create_producoes(db=db, registros=registros)
    return criados


@router.get(
    "",
    response_model=List[ProducaoOut]
)
def read_producoes(
    produto: Optional[List[str]] = Query([], description="Produto(s) para filtrar"),
    tipo: Optional[List[str]] = Query([], description="Tipo(s) para filtrar"),
    quantidadeMinima: Optional[int] = Query(None, description="Quantidade mínima"),
    quantidadeMaxima: Optional[int] = Query(None, description="Quantidade máxima"),
    ano: Optional[List[int]] = Query([], description="Ano(s) para filtrar"),
    db: Session = Depends(get_db),
):
    """
    GET /producao:
    - Lê do banco todos os registros de produção.
    - Aplica os filtros via query params (produto, tipo, quantidade e ano).
    """
    filtros_anos = ano if ano else None

    registros = crud_get_producoes(
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
    response_model=ProducaoOut,
    status_code=status.HTTP_201_CREATED
)
def create_producao_manual(
    registro: ProducaoBase,
    db: Session = Depends(get_db)
):
    """
    POST /producao:
    - Recebe manualmente (JSON) um registro ProducaoBase e insere no banco.
    - Retorna o registro criado (com id).
    """
    criado = crud_create_producao(db=db, registro=registro)
    return criado
