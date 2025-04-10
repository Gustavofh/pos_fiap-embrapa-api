import requests
from bs4 import BeautifulSoup
import pandas as pd
from unidecode import unidecode
from typing import List, Optional, Dict, Any


class EmbrapaScraper:
    """
    Classe responsável por realizar o scrape de dados do site vitibrasil.cnpuv.embrapa.br
    conforme configurações fornecidas em CLASSIFICATIONS.
    """

    BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.php"

    CLASSIFICATIONS = [
        {
            "url": "opcao=opt_02",
            "categoria": "producao",
            "classificacao": None,
            "key_column": "produto",
            "column_names": ["cultivar", "quantidade_kg", "tipo", "ano", "categoria", "classificacao"],
        },
        {
            "url": "opcao=opt_03&subopcao=subopt_01",
            "categoria": "processamento",
            "classificacao": "vinifera",
            "key_column": "cultivar",
            "column_names": ["cultivar", "quantidade_kg", "tipo", "ano", "categoria", "classificacao"],
        },
        {
            "url": "opcao=opt_03&subopcao=subopt_02",
            "categoria": "processamento",
            "classificacao": "americana_e_hibrida",
            "key_column": "cultivar",
            "column_names": ["cultivar", "quantidade_kg", "tipo", "ano", "categoria", "classificacao"],
        },
        {
            "url": "opcao=opt_03&subopcao=subopt_03",
            "categoria": "processamento",
            "classificacao": "uva_de_mesa",
            "key_column": "cultivar",
            "column_names": ["cultivar", "quantidade_kg", "tipo", "ano", "categoria", "classificacao"],
        },
        {
            "url": "opcao=opt_04",
            "categoria": "comercializacao",
            "classificacao": None,
            "key_column": "produto",
            "column_names": ["produto", "quantidade_l", "tipo", "ano", "categoria", "classificacao"],
        },
        {
            "url": "opcao=opt_05&subopcao=subopt_01",
            "categoria": "importacao",
            "classificacao": "vinho_de_mesa",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_05&subopcao=subopt_02",
            "categoria": "importacao",
            "classificacao": "espumante",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_05&subopcao=subopt_03",
            "categoria": "importacao",
            "classificacao": "uva_fresca",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_05&subopcao=subopt_04",
            "categoria": "importacao",
            "classificacao": "uva_passa",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_05&subopcao=subopt_05",
            "categoria": "importacao",
            "classificacao": "suco_de_uva",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_06&subopcao=subopt_01",
            "categoria": "exportacao",
            "classificacao": "vinho_de_mesa",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_06&subopcao=subopt_02",
            "categoria": "exportacao",
            "classificacao": "espumante",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_06&subopcao=subopt_03",
            "categoria": "exportacao",
            "classificacao": "uva_fresca",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
        {
            "url": "opcao=opt_06&subopcao=subopt_04",
            "categoria": "exportacao",
            "classificacao": "suco_de_uva",
            "key_column": "paises",
            "column_names": ["paises", "quantidade_kg", "valor_dol", "ano", "categoria", "classificacao"],
            "anos": [1970, 2024],
        },
    ]

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        """
        :param session: (opcional) objeto requests.Session para otimização de conexões.
        """
        self.session = session if session else requests.Session()

    def _request_data(self, url: str) -> Optional[BeautifulSoup]:
        """
        Realiza requisição GET à URL desejada e retorna um objeto BeautifulSoup, se sucesso.
        :param url: URL completa para scrape.
        :return: Objeto BeautifulSoup ou None, caso falhe.
        """
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"Resposta HTTP inesperada ({response.status_code}) para {url}")
                return None
        except requests.RequestException as e:
            print(f"Erro ao requisitar {url}: {e}")
            return None

    def _extract_data(self, soup: BeautifulSoup) -> pd.DataFrame:
        """
        Extrai dados da tabela class='tb_base tb_dados' em um BeautifulSoup e retorna um DataFrame.
        :param soup: Objeto BeautifulSoup contendo a página.
        :return: DataFrame com o conteúdo da tabela, ou vazio se nada for encontrado.
        """
        table_soup = soup.find('table', {'class': 'tb_base tb_dados'})
        if not table_soup:
            return pd.DataFrame()

        thead = table_soup.find('thead')
        if not thead:
            return pd.DataFrame()

        col_names: List[str] = []
        for row in thead.find_all('tr'):
            data_cols = [
                unidecode(th.get_text(strip=True).lower()).replace(" ", "_")
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

    def scrape_category(self, categoria: str) -> pd.DataFrame:
        """
        Percorre CLASSIFICATIONS, filtra pela categoria informada e faz requests para cada ano.
        Para cada página, extrai a tabela e unifica os dados em um DataFrame.
        
        :param categoria: ex: 'producao', 'processamento', etc.
        :return: DataFrame unificado com dados de todos os anos.
        """
        result_rows = []
        default_anos = range(1970, 2024)

        for conf in self.CLASSIFICATIONS:
            if conf.get("categoria") == categoria:
                cat = conf.get("categoria")
                classificacao = conf.get("classificacao")
                key_col = conf.get("key_column")

                # Determina range de anos
                if conf.get("anos"):
                    start, end = conf["anos"]
                    anos = range(start, end + 1)
                else:
                    anos = default_anos

                current_type: Optional[str] = None

                for ano in anos:
                    url_query = f"{self.BASE_URL}?{conf['url']}&ano={ano}"
                    print(f"Coletando {url_query}")

                    soup = self._request_data(url_query)
                    if not soup:
                        continue

                    df_page = self._extract_data(soup)
                    if df_page.empty:
                        continue

                    for _, row in df_page.iterrows():
                        produto = row[key_col]

                        if produto == produto.upper():
                            current_type = produto
                            continue

                        new_row = row.copy()

                        if key_col != "paises" and current_type:
                            new_row["tipo"] = unidecode(current_type.lower()).replace(" ", "_")

                        # Adiciona colunas extras
                        new_row["ano"] = ano
                        new_row["categoria"] = cat
                        new_row["classificacao"] = classificacao

                        result_rows.append(new_row)

        if not result_rows:
            return pd.DataFrame()

        df_final = pd.DataFrame(result_rows)

        table_original_cols = list(df_final.columns)
        for conf in self.CLASSIFICATIONS:
            if conf.get("categoria") == categoria:
                table_new_cols = conf.get('column_names')
        rename_map = dict(zip(table_original_cols, table_new_cols))
        print(rename_map)
        df_final.rename(columns=rename_map, inplace=True)
        df_final = df_final[table_new_cols].reset_index(drop=True)

        return df_final

