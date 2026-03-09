from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API Corporativa para Gestão de Ativos de TI e Logística.",
    version="1.0.0"
)

# Configurar o CORS para aceitar conexões do Frontend Next.js (mesmo rodando em PWA ou app nativo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, restringir para os domínios do Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bem-vindo ao Sistema Corporativo de Inventário de TI."}

@app.get("/health")
def health_check():
    return {"status": "ok", "system": settings.PROJECT_NAME}

from app.api.v1.routers import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
