import logging
import numpy as np
import pandas as pd

from app.scraper.scraper import EmbrapaScraper

logger = logging.getLogger(__name__)


def create_dataframe(
        scraper: EmbrapaScraper,
        url: str,
        main_cols: str,
        anos: list,
        numeric_cols: list = [],
        other_cols: list = ['tipo', 'ano'],
        tipo: str = None,
        caracteristica: bool = False
):
    """
    Extrai dados da tabela class='tb_base tb_dados' em um BeautifulSoup e
    retorna um DataFrame. Agora, marca cada linha com o 'item' correspondente
    (via coluna interna '__item'), mas só adiciona o item como linha se não houver subitems.
    """
    pd.set_option('future.no_silent_downcasting', True)

    columns = [main_cols] + numeric_cols + other_cols
    df = pd.DataFrame(columns=columns)

    for ano in anos:
        scraper.request_data(f"{url}&ano={ano}")
        raw_data = scraper.extract_data()

        for col in numeric_cols:
            raw_data[col] = (
                raw_data[col]
                .str.replace(".", "", regex=False)
                .replace("-", np.nan)
            )
        raw_data = raw_data.dropna(subset=numeric_cols, how="all")
        if raw_data.empty:
            continue

        if '__item' in raw_data.columns:
            if tipo:
                raw_data['tipo'] = tipo
            else:
                raw_data['tipo'] = raw_data['__item']

            if caracteristica:
                raw_data['caracteristica'] = raw_data['__item']
        else:
            if tipo:
                raw_data['tipo'] = tipo
            else:
                raw_data['tipo'] = None

            if caracteristica:
                raw_data['caracteristica'] = None

        raw_data['ano'] = f"{ano}"
        raw_data[main_cols] = [line.lower() for line in raw_data[main_cols]]

        if '__item' in raw_data.columns:
            raw_data = raw_data.drop(columns=['__item'])

        df = pd.concat([df, raw_data], ignore_index=True)

    return df
