import os
import pickle
import pandas as pd
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.v1.crud.predicao_producao import (
    create_predicao_producao,
    get_predicoes_producao
)
from app.v1.schemas.predicao_producao import (
    PredicaoProducaoCreate,
    PredicaoProducaoOut
)

router = APIRouter(prefix="/predicao/producao", tags=["Predição"])

MODEL_PATH = os.path.join("predict_models", "production_model.pkl")
try:
    with open(MODEL_PATH, "rb") as f:
        production_model = pickle.load(f)
except FileNotFoundError:
    production_model = None


@router.post(
    "",
    response_model=PredicaoProducaoOut,
    status_code=status.HTTP_201_CREATED
)
def predizer_producao(
    dados: PredicaoProducaoCreate,
    db: Session = Depends(get_db)
):
    """
    Gera a predição de produção (em litros) para um determinado produto, tipo e ano.
    1) Recebe JSON { produto, tipo, ano }.
    2) Usa o modelo carregado (production_model.predict) para estimar valor_previsto.
    3) Salva no banco (tabela predicao_producao) com create_predicao_producao.
    4) Retorna o objeto com id, produto, tipo, ano, valor_previsto e created_at.
    """

    if production_model is None:
        raise HTTPException(
            status_code=500,
            detail="Modelo de produção não encontrado no servidor."
        )

    try:
        df_input = pd.DataFrame([{
            "produto": dados.produto,
            "tipo": dados.tipo,
            "ano": int(dados.ano)
        }])
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Ano deve ser algo que possa converter para inteiro."
        )

    try:
        valor_previsto_arr = production_model.predict(df_input)
        valor_previsto = float(valor_previsto_arr[0])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar predição: {e}"
        )

    predicao_obj = create_predicao_producao(
        db=db,
        predicao_in=dados,
        valor_previsto=valor_previsto
    )

    return predicao_obj


@router.get(
    "",
    response_model=List[PredicaoProducaoOut]
)
def listar_predicoes_producao(
    db: Session = Depends(get_db)
):
    """
    Retorna todas as predições de produção já salvas.
    """
    resultados = get_predicoes_producao(db=db)
    return resultados
