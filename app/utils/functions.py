import requests
from bs4 import BeautifulSoup
import pandas as pd 

def build_query(dataset: str, filters) -> str:
    base_query = f"SELECT * FROM `your-project.your_dataset.{dataset}` WHERE 1=1"
    if filters.id:
        base_query += " AND product = @product"
    if filters.product:
        base_query += " AND product = @product"
    if filters.minQuantity is not None:
        base_query += " AND quantity >= @minQuantity"
    if filters.maxQuantity is not None:
        base_query += " AND quantity <= @maxQuantity"
    return base_query
    