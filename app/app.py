from fastapi import FastAPI
from app.v1.routes.producao import router as producao_router
from app.v1.routes.processamento import router as processamento_router
from app.v1.routes.comercializacao import router as comercializacao_router
from app.v1.routes.importacao import router as importacao_router
from app.v1.routes.exportacao import router as exportacao_router
from app.v1.routes.predicao_producao import router as predicao_producao_router
from app.v1.routes.predicao_exportacao import router as predicao_exportacao_router

app = FastAPI(
    title="Análises EMBRAPA",
    description="Coleta para análise de dados históricos da Viniticultura da EMBRAPA",
    version="1.0.0"
)

app.include_router(producao_router)
app.include_router(processamento_router)
app.include_router(comercializacao_router)
app.include_router(importacao_router)
app.include_router(exportacao_router)
app.include_router(predicao_producao_router)
app.include_router(predicao_exportacao_router)

@app.get("/")
async def root():
    return {"message": "Bem vindo!"}
