from fastapi import FastAPI
from app.v1.routes.producao import router as producao_router
from app.v1.routes.processamento import router as processamento_router
from app.v1.routes.testando_new import router as testando_new_router

app = FastAPI(title="API de Produções")

app.include_router(producao_router)
app.include_router(processamento_router)
app.include_router(testando_new_router)

@app.get("/")
async def root():
    return {"message": "bem vindo!"}
