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
    categoria: Optional[CategoriaResponse] = None
    created_at: Optional[Any] = None
    
    class Config:
        from_attributes = True

class AtivoCreate(AtivoBase):
    categoria_id: UUID

class AtivoUpdate(BaseModel):
    patrimonio: Optional[str] = Field(None, max_length=50)
    numero_serie: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    status: Optional[str] = None
    local_id: Optional[UUID] = None
    colaborador_id: Optional[UUID] = None
    especificacoes_tecnicas: Optional[Dict[str, Any]] = None
    observacoes: Optional[str] = None

class HistoricoSchema(BaseModel):
    id: UUID
    ativo_id: UUID
    usuario_id: UUID
    tipo_acao: str
    colaborador_destino_id: Optional[UUID] = None
    local_destino_id: Optional[UUID] = None
    observacao: Optional[str] = None
    data_hora: Any
    
    class Config:
        from_attributes = True

class AtribuirSchema(BaseModel):
    colaborador_id: UUID
    local_id: UUID
    observacao: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str
    observacao: Optional[str] = "Mudança manual de status via painel"
