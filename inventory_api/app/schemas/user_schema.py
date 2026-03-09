from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# DTOs Base para garantir que APIs não vazem a senha

class UserBase(BaseModel):
    email: EmailStr
    role: str = "colaborador"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    status: bool

    class Config:
        from_attributes = True

class ColaboradorBase(BaseModel):
    nome_completo: str
    email: EmailStr
    setor: Optional[str] = None
    cargo: Optional[str] = None

class ColaboradorCreate(ColaboradorBase):
    pass

class ColaboradorResponse(ColaboradorBase):
    id: UUID
    status: str
    
    class Config:
        from_attributes = True

class LocalSchema(BaseModel):
    id: UUID
    nome: str

    class Config:
        from_attributes = True
