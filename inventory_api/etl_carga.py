import asyncio
import pandas as pd
import uuid
from sqlalchemy.future import select
from app.db.session import async_session
from app.db.models import Ativo, Categoria, Local, Colaborador, User, HistoricoMovimentacao

async def rodar_carga():
    """ 
    Script de Migração: 
    Lê a planilha velha, cruza Chaves Estrangeiras, 
    Joga as 'sobras' (Memoria, CPU, HD) para a coluna inteligente JSONB e salva.
    """
    print("🚀 Iniciando Motor de Carga ETL do Inventário...")
    df = pd.read_csv("data_mock/planilha_legada.csv", keep_default_na=False)
    
    async with async_session() as db:
        
        # O Admin Master System fará essa carga
        result_usr = await db.execute(select(User).limit(1))
        system_user = result_usr.scalars().first()
        if not system_user:
            print("❌ ERRO: Necessário ter ao menos 1 usuário (Admin) no banco para assinar essa migração.")
            return

        sucesso = 0
        falhas = 0

        for index, row in df.iterrows():
            try:
                patrimonio = str(row['PATRIMONIO']).strip()
                if not patrimonio: continue
                
                # 1. Verifica se já existe para evitar crash
                existente = await db.execute(select(Ativo).filter(Ativo.patrimonio == patrimonio))
                if existente.scalars().first():
                    print(f"⚠️ Pulo: {patrimonio} já existe no sistema novo.")
                    continue

                # 2. Resolução Dinâmica de FKs (Cria se não existir, algo comum em migrações)
                
                # Categoria (Notebook, Celular)
                tipo = str(row['TIPO_EQUIPAMENTO']).strip()
                cat_result = await db.execute(select(Categoria).filter(Categoria.nome == tipo))
                categoria = cat_result.scalars().first()
                if not categoria:
                    categoria = Categoria(nome=tipo, prefixo_patrimonio=tipo[:3].upper())
                    db.add(categoria)
                    await db.flush()
                
                # Local
                local_nome = str(row['LOCAL']).strip()
                loc_result = await db.execute(select(Local).filter(Local.nome == local_nome))
                local = loc_result.scalars().first()
                if not local:
                    local = Local(nome=local_nome, endereco="Carregado via Carga Lote")
                    db.add(local)
                    await db.flush()
                    
                # Colaborador (Pode estar vazio se tiver no estoque)
                colaborador_id = None
                status_atual = 'estoque'
                colab_nome = str(row['NOME_COLABORADOR']).strip()
                
                if colab_nome:
                    col_result = await db.execute(select(Colaborador).filter(Colaborador.nome == colab_nome))
                    colaborador = col_result.scalars().first()
                    if not colaborador:
                        # Email placeholder
                        colaborador = Colaborador(nome=colab_nome, email=f"{colab_nome.split()[0].lower()}@nk3.com.br", departamento="Geral")
                        db.add(colaborador)
                        await db.flush()
                    colaborador_id = colaborador.id
                    status_atual = 'em_uso'
                
                # 3. O Poder do Híbrido: Empacotar os RESTOS em JSONB (Adeus Coluna Vazia do IP Phone)
                especificacoes = {}
                if row['MEMORIA_RAM']: especificacoes['memoria_ram'] = row['MEMORIA_RAM']
                if row['ARMAZENAMENTO']: especificacoes['armazenamento'] = row['ARMAZENAMENTO']
                if row['PROCESSADOR']: especificacoes['processador'] = row['PROCESSADOR']
                
                # 4. Criando Entidade Principal e Injetando o JSONB
                novo_ativo = Ativo(
                    patrimonio=patrimonio,
                    numero_serie=row['SERIAL'] if row['SERIAL'] else None,
                    marca=row['MARCA'],
                    modelo=row['MODELO'],
                    status=status_atual,
                    categoria_id=categoria.id,
                    local_id=local.id,
                    colaborador_id=colaborador_id,
                    especificacoes_tecnicas=especificacoes,
                    observacoes="📦 CARGA EM LOTE: Importado da Antiga Planilha CSV."
                )
                db.add(novo_ativo)
                await db.flush() # Salva rapido para gerar uuid

                # 5. Rastro Mestre (Auditoria obrigatoria)
                historico = HistoricoMovimentacao(
                    ativo_id=novo_ativo.id,
                    usuario_id=system_user.id,
                    tipo_acao="migracao_lote",
                    local_destino_id=local.id,
                    colaborador_destino_id=colaborador_id,
                    observacao="Migração Primária do Excel Legado"
                )
                db.add(historico)
                
                sucesso += 1

            except Exception as e:
                print(f"❌ Erro na linha {index} ({row['PATRIMONIO']}): {e}")
                falhas += 1
                
        # Commita a Transação (Transacional: Ou tudo, ou nada - Segurança ACID)
        await db.commit()
        print(f"✅ CARGA FINALIZADA! {sucesso} Ativos Portados com Sucesso. Falhas: {falhas}")

if __name__ == "__main__":
    asyncio.run(rodar_carga())
