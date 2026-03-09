from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

# Aqui validamos a entrada de tipos de Ativos. Ex: Notebook (Prefixo: NTB)
class CategoriaBase(BaseModel):
    nome: str
    prefixo_patrimonio: str = Field(..., max_length=10)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: UUID
    class Config:
        from_attributes = True

# Preparação avançada para a Sprint 2 (O Ativo e o JSON Dinâmico)
class AtivoBase(BaseModel):
    patrimonio: str = Field(..., max_length=50)
    numero_serie: Optional[str] = None
    marca: str
    modelo: str
    status: str
    local_id: UUID
    colaborador_id: Optional[UUID] = None
    especificacoes_tecnicas: Dict[str, Any] = {} # Aqui recebe o Processador, Memória, IMEI
    observacoes: Optional[str] = None

class AtivoResponse(AtivoBase):
    id: UUID
    class Config:
        from_attributes = True
