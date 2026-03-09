from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.db.session import get_db
from app.db.models import User

# O endpoint que o Swagger e o Next.js farão o POST automático para logar
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """ Dependência escudo: Quem tentar usar rota protegida sem JWT ou com JWT falso é bloqueado antes da lógica """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    if not user.status:
        raise HTTPException(status_code=403, detail="Usuário Inativo")
        
    return user

def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """ Escudo secundário: Permite acesso apenas para Admins """
    if current_user.role != "admin_ti":
        raise HTTPException(status_code=403, detail="Privilégios insuficientes para esta ação.")
    return current_user
