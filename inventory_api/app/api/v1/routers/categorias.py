from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Categoria
from app.schemas.ativo_schema import CategoriaResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CategoriaResponse])
async def listar_categorias(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ Retorna todos os tipos estruturais de ativos que a empresa gerencia. (ex: Monitor, Celular) """
    result = await db.execute(select(Categoria))
    categorias = result.scalars().all()
    return categorias
