from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.v1.crud.importacao import (
    create_importacoes,
    get_importacoes as crud_get_importacoes,
    create_importacao as crud_create_importacao
)
from app.core.database import get_db
from app.scraper.functions import create_dataframe
from app.scraper.scraper import EmbrapaScraper
from app.v1.schemas.importacao import ImportacaoBase, ImportacaoOut

router = APIRouter(prefix="/importacao", tags=["Importação"])
scraper = EmbrapaScraper()


@router.get(
    "/update",
    response_model=List[ImportacaoOut],
    status_code=status.HTTP_201_CREATED
)
def update_importacao(
    db: Session = Depends(get_db),
    ano: List[int] = Query(list(range(1970, 2025)), description="Repita o parâmetro para cada ano")
):
    """
    Rota /importacao/update:
    - Faz o scraping de TODOS os anos informados (default 1970–2024),
      gera o DataFrame completo (sem filtros do usuário) e salva tudo no banco.
    - Retorna a lista de ImportacaoOut dos registros recém-inseridos.
    """
    URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    config = {
        "main_cols": "paises",
        "numeric_cols": ['quantidade_kg', "valor_dolar"]
    }
    types = {
        "vinhos_de_mesa": f'{URL}?opcao=opt_05&subopcao=subopt_01',
        "espumantes": f'{URL}?opcao=opt_05&subopcao=subopt_02',
        "uvas_frescas": f'{URL}?opcao=opt_05&subopcao=subopt_03',
        "uvas_passas": f'{URL}?opcao=opt_05&subopcao=subopt_04',
        "suco_de_uva": f'{URL}?opcao=opt_05&subopcao=subopt_05',
    }

    df = pd.DataFrame(columns=['paises', 'quantidade_kg', 'valor_dolar', 'tipo', 'ano'])
    for tipo_, url in types.items():
        df_aux = create_dataframe(
            scraper=scraper,
            url=url,
            main_cols=config["main_cols"],
            numeric_cols=config["numeric_cols"],
            anos=ano,
            tipo=tipo_
        )
        df = pd.concat([df, df_aux], ignore_index=True)

    if df.empty:
        anos_str = ", ".join(map(str, ano))
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum dado encontrado para o(s) ano(s): {anos_str}"
        )

    registros: List[ImportacaoBase] = []
    for row in df.to_dict(orient="records"):
        item = ImportacaoBase(
            paises=row["paises"],
            quantidade_kg=int(row["quantidade_kg"]),
            valor_dolar=int(row["valor_dolar"]),
            tipo=row["tipo"],
            ano=str(row["ano"]),
        )
        registros.append(item)

    criados = create_importacoes(db=db, importacoes=registros)
    return criados


@router.get(
    "",
    response_model=List[ImportacaoOut]
)
def read_importacoes(
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
    Rota GET /importacao/:
    - Busca no banco todos os registros de importação.
    - Aplica os filtros fornecidos via query params.
    """
    filtros_anos = ano if ano else None

    registros = crud_get_importacoes(
        db=db,
        paises=pais or None,
        tipos=tipo or None,
        quantidade_minima=quantidadeMinima,
        quantidade_maxima=quantidadeMaxima,
        valor_minimo=valorMinimo,
        valor_maximo=valorMaximo,
        anos=filtros_anos,
    )

    return registros


@router.post(
    "",
    response_model=ImportacaoOut,
    status_code=status.HTTP_201_CREATED
)
def create_importacao_manual(
    importacao: ImportacaoBase,
    db: Session = Depends(get_db)
):
    """
    Rota POST /importacao/:
    - Recebe manualmente (JSON) um registro ImportacaoBase e insere no banco.
    - Retorna o registro criado (com id).
    """
    criado = crud_create_importacao(db=db, importacao=importacao)
    return criado
