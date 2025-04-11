from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from app.bigquery.bigquery import BigQueryConnector
from app.models.producao import Producao, ProducaoFilter

router = APIRouter(
    prefix="/producao",
    tags=["producao"]
)

@router.get("/data", response_model=List[Producao])
async def get_data(filters: ProducaoFilter = Depends()):
    """
    Retorna dados filtrados dinamicamente via Query Params.
    Exemplo: GET /producao/data?ano=2023&minQuantidade=1000
    """
    query = "SELECT * FROM `fiap-pos-tech-mle.dados_embrapa.producao` WHERE 1=1"

    if filters.ano is not None:
        query += f" AND ano = '{filters.ano}'"
    if filters.minQuantidade is not None:
        query += f" AND quantidade_kg >= {filters.minQuantidade}"
    if filters.maxQuantidade is not None:
        query += f" AND quantidade_kg <= {filters.maxQuantidade}"
    if filters.tipo is not None:
        query += f" AND tipo = '{filters.tipo}'"

    conn = BigQueryConnector()
    res = await conn.execute_query(query=query)
    rows = [dict(row) for row in res]
    producao_list = [Producao(**item) for item in rows]

    return producao_list
