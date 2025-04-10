from fastapi import APIRouter, HTTPException

from models.models import ProductData
from utils.functions import build_query
from bigquery.bigquery import BigQueryConnector


DATASET = "producao"

router = APIRouter(
    prefix="/producao",
    tags=["producao"]
)

@router.get('/data')
async def get_data(data: ProductData):
    query = build_query(dataset=DATASET, filters=data)
    conn = BigQueryConnector()
    await conn.execute_query(query=query)
    
    
    
    