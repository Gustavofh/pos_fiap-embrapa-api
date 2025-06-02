import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
from unidecode import unidecode
from typing import List, Optional, Dict, Any


class EmbrapaScraper:
    """
    Classe responsável por realizar o scrape de dados do site vitibrasil.cnpuv.embrapa.br
    conforme configurações fornecidas em CLASSIFICATIONS.
    """

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        """
        :param session: (opcional) objeto requests.Session para otimização de conexões.
        """
        self.soup = None
        self.session = session if session else requests.Session()
        self.url = "http://vitibrasil.cnpuv.embrapa.br/index.php"

    def request_data(self, url: str) -> Optional[BeautifulSoup]:
        """
        Realiza requisição GET à URL desejada e retorna um objeto BeautifulSoup, se sucesso.
        :param url: URL completa para scrape.
        :return: Objeto BeautifulSoup ou None, caso falhe.
        """
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            }
            response = self.session.get(url, headers=headers, timeout=30, verify=False)
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.text, 'html.parser')
                return None
            else:
                print(f"Resposta HTTP inesperada ({response.status_code}) para {url}")
                return None
        except requests.RequestException as e:
            print(f"Erro ao requisitar {url}: {e}")
            return None

    def extract_data(self) -> pd.DataFrame:
        """
        Extrai dados da tabela class='tb_base tb_dados' em um BeautifulSoup e retorna um DataFrame.
        :param soup: Objeto BeautifulSoup contendo a página.
        :return: DataFrame com o conteúdo da tabela, ou vazio se nada for encontrado.
        """
        table_soup = self.soup.find('table', {'class': 'tb_base tb_dados'})
        if not table_soup:
            return pd.DataFrame()

        thead = table_soup.find('thead')
        if not thead:
            return pd.DataFrame()

        col_names: List[str] = []
        for row in thead.find_all('tr'):
            data_cols = [
                unidecode(th.get_text(strip=True).lower()).replace(" ", "_").replace("(", "").replace(")", "").replace(
                    ".", "")
                for th in row.find_all('th')
            ]
            col_names.extend(data_cols)

        tbody = table_soup.find('tbody')
        if not tbody:
            return pd.DataFrame(columns=col_names)

        rows_data: List[List[str]] = []
        for row in tbody.find_all('tr'):
            cols = [td.get_text(strip=True) for td in row.find_all('td')]
            if len(cols) > 1:
                cols[0] = unidecode(cols[0]).replace(" ", "_")
                rows_data.append(cols)

        df = pd.DataFrame(rows_data, columns=col_names)
        return df
