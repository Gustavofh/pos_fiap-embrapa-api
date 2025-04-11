import os
import json
import asyncio
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter

load_dotenv()

class BigQueryConnector:
    def __init__(self):
        """
        Inicializa a conexão com o BigQuery utilizando as credenciais definidas na variável de ambiente 'CREDENTIALS_JSON'.
        
        :param project_id: ID do projeto no Google Cloud.
        :raises ValueError: Se a variável de ambiente não for encontrada ou ocorrer erro no parse do JSON.
        """
        credentials_json_str = os.getenv('CREDENTIALS_JSON')
        if not credentials_json_str:
            raise ValueError("A variável de ambiente 'CREDENTIALS_JSON' não foi encontrada.")

        try:
            credentials_json = json.loads(credentials_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON das credenciais: {e}")

        self.credentials = service_account.Credentials.from_service_account_info(credentials_json)
        self.project_id = os.getenv('PROJECT_ID')
        self.dataset_id = os.getenv('DATASET_ID')
        
        self.client = bigquery.Client(project=self.project_id, credentials=self.credentials)
    
    def load_dataframe_to_bigquery(self, df, table_id: str):
        bq_client = bigquery.Client(project=self.project_id, credentials=self.credentials)
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
        job = bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        print(f"[BIGQUERY] Tabela '{table_ref}' carregada com {len(df)} linhas.\n")
    
    
    async def execute_query(self, query: str):
        """
        Executa uma query no BigQuery utilizando parâmetros opcionais.
        
        :param query: String com a query SQL.
        :return: Resultados da query.
        :raises Exception: Propaga exceções ocorridas na execução da query.
        """ 
        query_job = self.client.query(query)
        return query_job.result()