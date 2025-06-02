import pandas as pd 
import numpy as np
from app.scraper.scraper import EmbrapaScraper
from app.bigquery.bigquery import BigQueryConnector

KEY_COLS = ['importacao']#, 'processamento', 'comercializacao', 'importacao', 'exportacao']


for key in KEY_COLS:
    scraper = EmbrapaScraper()
    bq_loader = BigQueryConnector()

    df_result = scraper.scrape_category(categoria=key)
    

    
    df_result['paises'] = df_result['paises'].astype('str')
    df_result['quantidade_kg'] = df_result['quantidade_kg'].str.replace('.', '').replace('nd', np.nan).replace('*', np.nan).astype('float')
    df_result['valor_dol'] = df_result['valor_dol'].str.replace('.', '').replace('nd', np.nan).replace('*', np.nan).astype('float')
    df_result['ano'] = df_result['ano'].astype('str')
    df_result['categoria'] = df_result['categoria'].astype('str')
    df_result['caracteristica'] = df_result['caracteristica'].astype('str')
    
    bq_loader.load_dataframe_to_bigquery(df_result, key)
