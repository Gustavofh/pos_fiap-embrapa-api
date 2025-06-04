import pickle
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.v1.crud.predicao_exportacao import (
    create_predicao_exportacao,
    get_predicoes_exportacao
)
from app.v1.schemas.predicao_exportacao import (
    PredicaoExportacaoCreate,
    PredicaoExportacaoOut
)

router = APIRouter(prefix="/predicao/exportacao", tags=["Predição"])

MODEL_PATH = os.path.join("predict_models", "export_value_model.pkl")
try:
    with open(MODEL_PATH, "rb") as f:
        export_value_model = pickle.load(f)
except FileNotFoundError:
    export_value_model = None


@router.post(
    "",
    response_model=PredicaoExportacaoOut,
    status_code=status.HTTP_201_CREATED
)
def predizer_exportacao(
    dados: PredicaoExportacaoCreate,
    db: Session = Depends(get_db)
):
    """
    Gera a predição de valor de exportação (em dólar) para um dado país, quantidade_kg e tipo.
    1) Recebe JSON { pais, quantidade_kg, tipo }.
    2) Monta DataFrame ou vetor conforme o modelo export_value_model.
    3) Chama export_value_model.predict(...) → valor_previsto.
    4) Salva no banco via create_predicao_exportacao.
    5) Retorna o registro salvo.
    """
    if export_value_model is None:
        raise HTTPException(
            status_code=500,
            detail="Modelo de valor de exportação não encontrado no servidor."
        )

    # Para muitos modelos scikit-learn, basta um DataFrame de uma linha
    import pandas as pd

    try:
        df_input = pd.DataFrame([{
            "pais": dados.pais,
            "quantidade_kg": dados.quantidade_kg,
            "tipo": dados.tipo
        }])
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Dados de entrada inválidos para formar DataFrame."
        )

    try:
        valor_previsto_arr = export_value_model.predict(df_input)
        valor_previsto = float(valor_previsto_arr[0])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar predição: {e}"
        )

    predicao_obj = create_predicao_exportacao(
        db=db,
        predicao_in=dados,
        valor_previsto=valor_previsto
    )

    return predicao_obj


@router.get(
    "",
    response_model=List[PredicaoExportacaoOut]
)
def listar_predicoes_exportacao(
    db: Session = Depends(get_db)
):
    """
    Retorna todas as predições de exportação já salvas.
    """
    resultados = get_predicoes_exportacao(db=db)
    return resultados
