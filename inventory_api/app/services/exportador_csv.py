import csv
import os
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.db.models import Ativo, Categoria, Local

EXPORT_FILE_PATH = "Controle_Estoque_NK3.csv"

async def exportar_para_csv():
    """
    Lê os ativos do banco de dados e exporta para um arquivo CSV
    na raiz do projeto, atuando como um backup/relatório automático.
    """
    try:
        async with AsyncSessionLocal() as db:
            # Busca todos os ativos fazendo um join implícito ou explícito
            # Aqui, vamos carregar as relações para pegar os nomes em vez dos IDs
            from sqlalchemy.orm import selectinload
            
            query = select(Ativo).options(
                selectinload(Ativo.categoria),
                selectinload(Ativo.local)
            )
            result = await db.execute(query)
            ativos = result.scalars().all()

            # Prepara os dados para o CSV
            dados = []
            for ativo in ativos:
                dados.append([
                    ativo.patrimonio,
                    ativo.marca,
                    ativo.modelo,
                    ativo.numero_serie or "N/A",
                    ativo.status,
                    ativo.categoria.nome if ativo.categoria else "N/A",
                    ativo.local.nome if ativo.local else "N/A",
                    ativo.observacoes or ""
                ])

            # Cabeçalhos do Excel
            cabecalhos = [
                "Patrimônio", "Marca", "Modelo", "Número de Série", 
                "Status", "Categoria", "Local Base", "Observações"
            ]

            # Escreve o arquivo
            with open(EXPORT_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';') # Ponto e vírgula é melhor para Excel BR
                writer.writerow(cabecalhos)
                writer.writerows(dados)
                
            print(f"[SUCESSO] Arquivo {EXPORT_FILE_PATH} atualizado com sucesso ({len(ativos)} registros).")
            return True

    except Exception as e:
        print(f"[ERRO] Erro ao exportar para CSV: {e}")
        return False
