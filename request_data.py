import pandas as pd 
from app.scraper.scraper import EmbrapaScraper
from app.bigquery.bigquery import BigQueryConnector

KEY_COLS = ['producao', 'processamento', 'comercializacao', 'importacao', 'exportacao']


for key in KEY_COLS:
    scraper = EmbrapaScraper()
    bq_loader = BigQueryConnector()

    df_result = scraper.scrape_category(categoria=key)
    bq_loader.load_dataframe_to_bigquery(df_result, key)
