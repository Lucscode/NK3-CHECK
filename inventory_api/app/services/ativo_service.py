import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import Ativo, HistoricoMovimentacao
from app.schemas.ativo_schema import AtivoCreate, AtivoUpdate
from app.services.exportador_csv import exportar_para_csv
import asyncio

async def criar_ativo(db: AsyncSession, ativo_data: AtivoCreate, usuario_id: str):
    # Regra 1 e 2: Verifica Unicidade de Patrimônio e Serial
    result_patrimonio = await db.execute(select(Ativo).filter(Ativo.patrimonio == ativo_data.patrimonio))
    if result_patrimonio.scalars().first():
        raise HTTPException(status_code=400, detail="Patrimônio já cadastrado.")
    
    if ativo_data.numero_serie:
        result_serial = await db.execute(select(Ativo).filter(Ativo.numero_serie == ativo_data.numero_serie))
        if result_serial.scalars().first():
            raise HTTPException(status_code=400, detail="Número de série já cadastrado.")
            
    # Cria o Equipamento
    novo_ativo = Ativo(**ativo_data.model_dump())
    db.add(novo_ativo)
    await db.flush() # Salva temporariamente para pegar o ID real
    
    # Regra 5: Hitórico obrigatório na criação
    historico = HistoricoMovimentacao(
        ativo_id=novo_ativo.id,
        usuario_id=usuario_id,
        tipo_acao="criacao",
        local_destino_id=novo_ativo.local_id,
        observacao="Equipamento cadastrado no sistema."
    )
    db.add(historico)
    await db.commit()
    await db.refresh(novo_ativo)
    
    # Executa a geração de relatório em background (fire and forget)
    asyncio.create_task(exportar_para_csv())
    
    return novo_ativo

async def mudar_status_ativo(
    db: AsyncSession, 
    ativo_id: uuid.UUID, 
    novo_status: str, 
    usuario_id: uuid.UUID, 
    observacao: str
):
    result = await db.execute(select(Ativo).filter(Ativo.id == ativo_id))
    ativo = result.scalars().first()
    
    if not ativo:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado.")
        
    status_antigo = ativo.status
    ativo.status = novo_status
    
    # Se estragou, tiramos da mão de quem tava
    if novo_status == "em_manutencao" or novo_status == "descartado":
         ativo.colaborador_id = None
         
    # Registrar Rastro (Auditoria Logística)
    historico = HistoricoMovimentacao(
        ativo_id=ativo.id,
        usuario_id=usuario_id,
        tipo_acao=f"mudanca_status:{status_antigo}->{novo_status}",
        observacao=observacao
    )
    db.add(historico)
    await db.commit()
    await db.refresh(ativo)
    
    # Atualiza o arquivo CSV assincronamente
    asyncio.create_task(exportar_para_csv())
    
    return ativo
