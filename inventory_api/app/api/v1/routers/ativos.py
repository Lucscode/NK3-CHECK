from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import User, Ativo
from app.schemas.ativo_schema import AtivoCreate, AtivoResponse
from app.services.ativo_service import criar_ativo

router = APIRouter()

@router.get("/", response_model=List[AtivoResponse])
async def listar_ativos(
    status: Optional[str] = None,
    categoria_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os equipamentos de TI, com paginação para segurar 50.000+ máquinas sem travar.
    Possibilita filtrar por Status (ex: em_uso) e anexará a Categoria original na mesma chamada Join.
    """
    query = select(Ativo).options(joinedload(Ativo.categoria))
    
    if status is not None:
        query = query.filter(Ativo.status == status)
    if categoria_id is not None:
         query = query.filter(Ativo.categoria_id == categoria_id)
         
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    ativos = result.scalars().all()
    return ativos

@router.post("/", response_model=AtivoResponse)
async def adicionar_ativo(
    ativo_in: AtivoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Post Base: Insere e ativa regra de negócio que força colocar na tabela Historico de Auditoria """
    novo = await criar_ativo(db=db, ativo_data=ativo_in, usuario_id=current_user.id)
    return novo

@router.get("/{id}", response_model=AtivoResponse)
async def detalhar_ativo(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Ficha Completa: Usado ao clicar na linha da tabela do React """
    result = await db.execute(select(Ativo).options(joinedload(Ativo.categoria)).filter(Ativo.id == id))
    ativo = result.scalars().first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return ativo

from app.schemas.ativo_schema import AtribuirSchema
from app.services.ativo_service import mudar_status_ativo
from app.db.models import HistoricoMovimentacao

@router.post("/{id}/atribuir")
async def atribuir_ativo_colaborador(
    id: str,
    dados: AtribuirSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Regra de Negócio: Impede entregar equipamento estragado ou descartado e gera log. """
    result = await db.execute(select(Ativo).filter(Ativo.id == id))
    ativo = result.scalars().first()
    
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
        
    if ativo.status in ["em_manutencao", "descartado"]:
        raise HTTPException(status_code=400, detail="Equipamento quebrado ou descartado não pode ser entregue.")
        
    ativo.colaborador_id = dados.colaborador_id
    ativo.local_id = dados.local_id
    ativo.status = "em_uso"
    
    historico = HistoricoMovimentacao(
        ativo_id=ativo.id,
        usuario_id=current_user.id,
        tipo_acao="atribuicao",
        colaborador_destino_id=dados.colaborador_id,
        local_destino_id=dados.local_id,
        observacao=dados.observacao
    )
    db.add(historico)
    await db.commit()
    return {"message": "Equipamento atribuído com sucesso."}

@router.post("/{id}/recolher")
async def recolher_ativo(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Regra de Logística: Tira do colaborador, devolve para a TI com Status: Estoque """
    ativo = await mudar_status_ativo(db, id, "estoque", current_user.id, "Equipamento recolhido para a matriz TI")
    return {"message": f"Ativo devolvido para o estoque."}

from app.schemas.ativo_schema import DanoMobileSchema
@router.post("/triagem-mobile-mock")
async def registrar_avaria_mobile(
    payload: DanoMobileSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Endpoint dedicado para atender ao celular PWA do Técnico (Triagem Logística e Câmera) """
    
    # 1. Encontra a máquina pela etiqueta bipada
    result = await db.execute(select(Ativo).filter(Ativo.patrimonio == payload.patrimonio))
    ativo = result.scalars().first()
    
    if not ativo:
         raise HTTPException(status_code=404, detail="Patrimônio não localizado no estoque global.")
    
    # 2. Chama a regra de negócio poderosa: muda o status e recorta a posse do usuário anterior
    ativo_atualizado = await mudar_status_ativo(
        db=db,
        ativo_id=ativo.id,
        novo_status=payload.status,
        usuario_id=current_user.id,
        observacao=f"AVARIA (App Mobile). Dano relatado: {payload.observacao_dano}. Evidência: {payload.foto_nome}"
    )
    
    return {"message": "Avaria registrada e status logístico atualizado.", "patrimonio": ativo_atualizado.patrimonio}
