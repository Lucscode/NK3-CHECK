from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Local
from app.schemas.user_schema import LocalSchema
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[LocalSchema])
async def listar_locais(
    db: AsyncSession = Depends(get_db),
    # Ao injetar esta dependência, a rota fica fechada a cadeado. Só com JWT o Front entra aqui.
    current_user = Depends(get_current_user) 
):
    """
    Lista todos os locais físicos da empresa para o preenchimento do `<select>` no Front-end 
    no momento do preenchimento da ficha técnica da máquina.
    """
    result = await db.execute(select(Local))
    locais = result.scalars().all()
    return locais
