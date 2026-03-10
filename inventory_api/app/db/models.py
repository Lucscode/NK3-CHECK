import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

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

class Ativo(Base):
    __tablename__ = "ativos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patrimonio = Column(String(50), unique=True, index=True, nullable=False)
    numero_serie = Column(String(100), unique=True, index=True, nullable=True)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias_ativo.id"), nullable=False)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    status = Column(String(50), default="estoque") # estoque, em_uso, em_manutencao, reservado, descartado
    colaborador_id = Column(UUID(as_uuid=True), ForeignKey("colaboradores.id"), nullable=True)
    local_id = Column(UUID(as_uuid=True), ForeignKey("locais.id"), nullable=False)
    especificacoes_tecnicas = Column(JSONB, default=dict) # O coração da flexibilidade
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    categoria = relationship("Categoria")
    colaborador = relationship("Colaborador")
    local = relationship("Local")

class AtivoImagem(Base):
    __tablename__ = "ativo_imagens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey("ativos.id"), nullable=False)
    url_imagem = Column(String(500), nullable=False)
    tipo = Column(String(50)) # frontal, traseira, avaria, termo_assinado
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class HistoricoMovimentacao(Base):
    __tablename__ = "historico_movimentacoes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ativo_id = Column(UUID(as_uuid=True), ForeignKey("ativos.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # Quem fez a ação no sistema
    tipo_acao = Column(String(50), nullable=False) # criacao, atribuicao, devolucao, manutencao, descarte
    colaborador_destino_id = Column(UUID(as_uuid=True), ForeignKey("colaboradores.id"), nullable=True)
    local_destino_id = Column(UUID(as_uuid=True), ForeignKey("locais.id"), nullable=True)
    observacao = Column(Text, nullable=True)
    data_hora = Column(DateTime, default=datetime.utcnow)
