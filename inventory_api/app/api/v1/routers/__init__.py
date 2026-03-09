from fastapi import APIRouter
from . import auth

# Mestre dos roteadores: Aqui nós colamos as rotas de todas as pontas 
# para plugar na raiz do sistema
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["🔒 Autenticação e Segurança"])
from . import locais # Importamos depois pq se o init estiver vazio ele cresce modularmente
api_router.include_router(locais.router, prefix="/locais", tags=["🏢 Locais (Almoxarifados)"])

from . import categorias
api_router.include_router(categorias.router, prefix="/categorias", tags=["🏷️  Categorias de Ativos"])

# Futuramente:
# api_router.include_router(ativos.router, prefix="/ativos", tags=["💻 Ativos de TI (Hardware)"])
# api_router.include_router(licencas.router, prefix="/licencas", tags=["🔑 Licenças (Software)"])
# api_router.include_router(dashboard.router, prefix="/dashboard", tags=["📊 Dashboards"])
