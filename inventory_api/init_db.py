import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.models import Base, User
from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash

async def init_db():
    print("Iniciando criação das tabelas no Banco de Dados...")
    engine = create_async_engine(settings.DATABASE_URI, echo=False)
    
    async with engine.begin() as conn:
        print("Trimming tabelas antigas se existirem...")
        # await conn.run_sync(Base.metadata.drop_all) # Descomente se quiser limpar tudo antes
        print("Criando tabelas novas...")
        await conn.run_sync(Base.metadata.create_all)
        
    print("Tabelas criadas com sucesso!")
    
    # Criar um usuário Master Admin se não existir
    async with AsyncSessionLocal() as db:
        from sqlalchemy.future import select
        result = await db.execute(select(User).filter(User.email == "admin@nk3.com.br"))
        admin = result.scalars().first()
        
        if not admin:
            print("Criando usuário admin padrão...")
            novo_admin = User(
                email="admin@nk3.com.br",
                password_hash=get_password_hash("admin123"), # Senha provisória
                role="admin_ti"
            )
            db.add(novo_admin)
            await db.commit()
            print("Usuário Admin criado (admin@nk3.com.br / admin123)")
        else:
            print("Usuário Admin já existe.")

        # Verificar Categorias Fixas
        from app.db.models import Categoria, Local
        res_cat = await db.execute(select(Categoria))
        if not res_cat.scalars().first():
            print("Criando categorias padrão...")
            cats = [
                Categoria(nome="Notebook / Laptop", prefixo_patrimonio="NTB"),
                Categoria(nome="Desktop / Gabinete", prefixo_patrimonio="DSK"),
                Categoria(nome="Monitor", prefixo_patrimonio="MNT"),
                Categoria(nome="Smartphone / Celular", prefixo_patrimonio="CEL"),
                Categoria(nome="Periférico / Outros", prefixo_patrimonio="PRF")
            ]
            db.add_all(cats)
            await db.commit()

        # Verificar Locais Fixos
        res_loc = await db.execute(select(Local))
        if not res_loc.scalars().first():
            print("Criando locais padrão...")
            locs = [
                Local(nome="Matriz - TI (Estoque Base)"),
                Local(nome="Filial Norte"),
                Local(nome="Home Office (Campo)")
            ]
            db.add_all(locs)
            await db.commit()
            
        print("Tabelas de suporte (Categorias e Locais) verificadas e populadas se necessário!")

if __name__ == "__main__":
    asyncio.run(init_db())
