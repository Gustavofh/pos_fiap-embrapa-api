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
    pd.set_option('future.no_silent_downcasting', True)

    columns = [main_cols] + numeric_cols + other_cols
    df = pd.DataFrame(columns=columns)
    for ano in anos:
        scraper.request_data(url=f"{url}&ano={ano}")
        raw_data = scraper.extract_data()
        for col in numeric_cols:
            raw_data[col] = (
                raw_data[col]
                .str.replace(".", "", regex=False)
                .replace("-", np.nan)
            )

        # if raw_data[numeric_cols[0]].isna().all() and ano >= 2023:
        if tipo:
            raw_data['tipo'] = tipo
        else:
            mask_upper = raw_data[main_cols].str.isupper()
            raw_data['tipo'] = raw_data[main_cols].where(mask_upper).ffill().str.lower()
            raw_data = raw_data[~mask_upper].reset_index(drop=True)

        if caracteristica:
            mask_upper = raw_data[main_cols].str.isupper()
            raw_data['caracteristica'] = raw_data[main_cols].where(mask_upper).ffill().str.lower()
            raw_data = raw_data[~mask_upper].reset_index(drop=True)

        raw_data['ano'] = f"{ano}"

        raw_data[main_cols] = [line.lower() for line in raw_data[main_cols]]
        df = pd.concat([df, raw_data], ignore_index=True)

        logging.info(f"Coletando dados do ano {ano}")
        print(f"Coletando dados do ano {ano}")
        if tipo:
            logging.info(f"Coletando dados para o tipo {tipo}\n")
            print(f"Coletando dados para o tipo {tipo}\n")
    return df
