from fastapi import FastAPI
from app.v1.routes.producao import router as producao_router
from app.v1.routes.processamento import router as processamento_router
from app.v1.routes.comercializacao import router as comercializacao_router
from app.v1.routes.importacao import router as importacao_router
from app.v1.routes.exportacao import router as exportacao_router

app = FastAPI(title="API de Produções")

app.include_router(producao_router)
app.include_router(processamento_router)
app.include_router(comercializacao_router)
app.include_router(importacao_router)
app.include_router(exportacao_router)

@app.get("/")
async def root():
    return {"message": "bem vindo!"}
