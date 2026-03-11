import asyncio
import pandas as pd
import uuid
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.db.models import Ativo, Categoria, Local, Colaborador, User, HistoricoMovimentacao

async def rodar_carga():
    """ 
    Script de Migração Adaptado para a Planilha Real do Cliente:
    Mapeia os nomes das colunas enviados na imagem.
    """
    print("Iniciando Motor de Carga ETL do Inventário...")
    df = pd.read_csv("data_mock/planilha_legada.csv", keep_default_na=False)
    
    # Normalizar os nomes das colunas (remover espaços extras nas pontas)
    df.columns = df.columns.str.strip()

    async with AsyncSessionLocal() as db:
        
        # O Admin Master System fará essa carga
        result_usr = await db.execute(select(User).limit(1))
        system_user = result_usr.scalars().first()
        if not system_user:
            print("ERRO: Necessário ter ao menos 1 usuário (Admin) no banco para assinar essa migração.")
            return

        sucesso = 0
        falhas = 0

        for index, row in df.iterrows():
            try:
                # Função segura para pegar valor da coluna se ela existir na planilha
                def get_val(col_names):
                    for col in col_names:
                        if col in df.columns:
                            val = row[col]
                            return str(val).strip() if pd.notna(val) and str(val).strip() != "" else None
                    return None

                # Mapeamento Flexível
                patrimonio = get_val(['Nome da máquina', 'Nome da máqu', 'PATRIMONIO', 'Hostname', 'Patrimonio'])
                if not patrimonio: 
                    continue # Se não tem nome da máquina, pula a linha
                
                # 1. Verifica se já existe
                existente = await db.execute(select(Ativo).filter(Ativo.patrimonio == patrimonio))
                if existente.scalars().first():
                    print(f"Pulo: {patrimonio} já existe no sistema novo.")
                    continue

                # 2. Resolução Dinâmica de FKs
                
                # Categoria (Como não vi na imagem, vamos tentar achar ou usar um padrão)
                tipo = get_val(['Tipo de Equipamento', 'Tipo', 'Categoria', 'TIPO_EQUIPAMENTO']) or 'Equipamento TI'
                cat_result = await db.execute(select(Categoria).filter(Categoria.nome == tipo))
                categoria = cat_result.scalars().first()
                if not categoria:
                    # Cria a categoria com o prefixo sendo as 3 primeiras letras
                    prefixo = tipo[:3].upper() if len(tipo) >= 3 else 'EQP'
                    categoria = Categoria(nome=tipo, prefixo_patrimonio=prefixo)
                    db.add(categoria)
                    await db.flush()
                
                # Local
                local_nome = get_val(['Local', 'LOCAL']) or 'Não Informado'
                loc_result = await db.execute(select(Local).filter(Local.nome == local_nome))
                local = loc_result.scalars().first()
                if not local:
                    local = Local(nome=local_nome)
                    db.add(local)
                    await db.flush()
                    
                # Colaborador e Status
                colab_nome = get_val(['Colaborador', 'NOME_COLABORADOR'])
                status_planilha = get_val(['Status', 'STATUS'])
                colaborador_id = None
                
                # Lógica para Status: Se tem colaborador, está em_uso, senão está livre/estoque
                status_atual = 'estoque'
                if colab_nome and colab_nome.upper() not in ['ESTOQUE', 'LIVRE', 'TI', '-', 'N/A']:
                    col_result = await db.execute(select(Colaborador).filter(Colaborador.nome_completo == colab_nome))
                    colaborador = col_result.scalars().first()
                    if not colaborador:
                        # Email placeholder
                        email_base = colab_nome.split()[0].lower() if len(colab_nome.split()) > 0 else 'usuario'
                        colaborador = Colaborador(nome_completo=colab_nome, email=f"{email_base}@nk3.com.br", setor="Geral")
                        db.add(colaborador)
                        await db.flush()
                    colaborador_id = colaborador.id
                    status_atual = 'em_uso'
                elif status_planilha and 'ESTOQUE' in status_planilha.upper():
                    status_atual = 'estoque'
                elif status_planilha and ('MANUTEN' in status_planilha.upper() or 'DEFEITO' in status_planilha.upper()):
                    status_atual = 'manutencao'
                
                # Especificações Técnicas Híbridas (O que sobrar vai para o JSON)
                especificacoes = {}
                memoria = get_val(['Memória', 'Memoria', 'MEMORIA_RAM'])
                if memoria: especificacoes['memoria_ram'] = memoria
                
                disco = get_val(['Disco', 'ARMAZENAMENTO', 'Armazenamento'])
                if disco: especificacoes['armazenamento'] = disco
                
                processador = get_val(['Processador', 'PROCESSADOR'])
                if processador: especificacoes['processador'] = processador
                
                so = get_val(['Sistema Operacional', 'SO'])
                if so: especificacoes['sistema_operacional'] = so
                
                garantia = get_val(['Data fim de Garant', 'Data fim de Garantia', 'Garantia'])
                if garantia: especificacoes['data_fim_garantia'] = garantia
                
                # Observações Gerais
                obs_parts = []
                obs = get_val(['Observação', 'OBS'])
                if obs: obs_parts.append(f"Obs legada: {obs}")
                
                novo_usado = get_val(['Novo ou usado', 'Novo ou usad'])
                if novo_usado: obs_parts.append(f"Condição Carga: {novo_usado}")
                
                licenca = get_val(['Licença Antivírus'])
                if licenca: obs_parts.append(f"Licença AV: {licenca}")

                contato = get_val(['Contato'])
                if contato: obs_parts.append(f"Contato: {contato}")

                termo = get_val(['Termo de responsa', 'Termo de responsabilidade'])
                if termo: obs_parts.append(f"Termo: {termo}")

                nf = get_val(['Nota Fiscal'])
                if nf: obs_parts.append(f"NF: {nf}")

                observacoes_finais = " | ".join(obs_parts) if obs_parts else "📦 CARGA EM LOTE: Importado da Antiga Planilha CSV."

                # 4. Criando Entidade Principal
                novo_ativo = Ativo(
                    patrimonio=patrimonio,
                    numero_serie=get_val(['Numero de série', 'Número de série', 'SERIAL', 'Serial']),
                    marca=get_val(['Marca', 'MARCA']),
                    modelo=get_val(['Modelo', 'MODELO']),
                    status=status_atual,
                    categoria_id=categoria.id,
                    local_id=local.id,
                    colaborador_id=colaborador_id,
                    especificacoes_tecnicas=especificacoes,
                    observacoes=observacoes_finais
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
                patrimonio_err = get_val(['Nome da máquina', 'Nome da máqu', 'PATRIMONIO']) or 'Desconhecido'
                print(f"Erro na linha {index} (Ativo: {patrimonio_err}): {e}")
                falhas += 1
                
        # Commita a Transação (Segurança ACID)
        await db.commit()
        print(f"CARGA FINALIZADA! {sucesso} Ativos Portados com Sucesso. Falhas: {falhas}")

if __name__ == "__main__":
    asyncio.run(rodar_carga())
