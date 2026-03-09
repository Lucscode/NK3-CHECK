import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="colaborador") # Valores: admin_ti, tecnico, gestor, colaborador
    status = Column(Boolean, default=True) # Ativo (True) ou Inativo/Demtido (False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Colaborador(Base):
    __tablename__ = "colaboradores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    setor = Column(String(100))
    cargo = Column(String(100))
    status = Column(String(50), default="ativo") # Valores: ativo, desligado
    created_at = Column(DateTime, default=datetime.utcnow)

class Local(Base):
    __tablename__ = "locais"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False) # Ex: Estoque Matriz, Sala Servidor
    created_at = Column(DateTime, default=datetime.utcnow)

class Categoria(Base):
    __tablename__ = "categorias_ativo"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False) # Ex: Notebook, Celular
    prefixo_patrimonio = Column(String(10), nullable=False) # Ex: NTB, CEL
    created_at = Column(DateTime, default=datetime.utcnow)
