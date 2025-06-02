from typing import List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode


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
        Extrai dados da tabela class='tb_base tb_dados' em um BeautifulSoup e
        retorna um DataFrame. Ajusta para lidar com páginas que têm apenas linhas simples
        (sem classes 'tb_item' ou 'tb_subitem'), como importação/exportação.
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
                unidecode(th.get_text(strip=True).lower())
                .replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
                for th in row.find_all('th')
            ]
            col_names.extend(data_cols)

        tbody = table_soup.find('tbody')
        if not tbody:
            return pd.DataFrame(columns=col_names)

        rows_data: List[List[str]] = []
        current_item: str | None = None
        skip_item_row = False

        trs = tbody.find_all('tr')
        i = 0
        while i < len(trs):
            row = trs[i]
            tds = row.find_all('td')

            if not tds[0].get("class"):
                cols = [td.get_text(strip=True).replace(".", "").replace(",", "") for td in tds]
                rows_data.append(cols)
            else:
                if len(tds) > 1:
                    raw_nome = tds[0].get_text(strip=True)
                    raw_qtd = tds[1].get_text(strip=True)
                    nome_fmt = unidecode(raw_nome).replace(" ", "_").lower()
                    td_classes = tds[0].get("class", [])

                    if "tb_item" in td_classes:
                        current_item = nome_fmt

                        skip_item_row = False
                        if i + 1 < len(trs):
                            next_td_classes = trs[i + 1].find_all('td')[0].get("class", [])
                            if "tb_subitem" in next_td_classes:
                                skip_item_row = True

                        if not skip_item_row:
                            row_list: List[str] = [nome_fmt, raw_qtd, current_item]
                            rows_data.append(row_list)

                    elif "tb_subitem" in td_classes:
                        row_list: List[str] = [nome_fmt, raw_qtd, current_item]
                        rows_data.append(row_list)

            i += 1

        if rows_data and not trs[0].find_all('td')[0].get("class"):
            df = pd.DataFrame(rows_data, columns=col_names)
        else:
            final_cols = col_names + ["__item"]
            df = pd.DataFrame(rows_data, columns=final_cols)

        if 'valor_us$' in df.columns:
            df = df.rename(columns={'valor_us$': 'valor_dolar'})

        print(df)
        return df

