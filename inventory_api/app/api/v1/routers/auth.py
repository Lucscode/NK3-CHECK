from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import User
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/login")
async def login_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """ Endpoint público que devolve o Token Portador (Bearer) válido para o Front usar. """
    
    # Busca assíncrona o usuário pelo 'username' que (no nosso caso) é o email do cara.
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Combinação de E-mail/Senha Incorreta"
        )
        
    if not user.status:
        raise HTTPException(status_code=400, detail="Acesso bloqueado. Conta inativa.")
        
    # Dá tudo certo, nós geramos o token mágico
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }
