from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.core.config import settings
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API Corporativa para Gestão de Ativos de TI e Logística.",
    version="1.0.0"
)

# Configurando as pastas contendo os HTML do painel (App "Monólito/Decoupled Híbrido")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas do FrontEnd renderizadas pelo Servidor Backend
@app.get("/login", response_class=HTMLResponse)
async def view_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/scanner", response_class=HTMLResponse)
async def view_scanner_mobile(request: Request):
    return templates.TemplateResponse("scanner.html", {"request": request})

@app.get("/ficha/{id}", response_class=HTMLResponse)
async def view_ficha_tecnica(request: Request, id: str):
    return templates.TemplateResponse("ficha_tecnica.html", {"request": request, "id": id})

@app.get("/", response_class=HTMLResponse)
async def view_raiz(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/health")
def health_check():
    return {"status": "ok", "system": settings.PROJECT_NAME}

from app.api.v1.routers import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
