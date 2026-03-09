from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

# Engine assíncrono para garantir alta performance concorrencial no Banco de Dados
engine = create_async_engine(settings.DATABASE_URI, echo=False)

# Session local para as injeções de dependência no FastAPI
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    """ Dependency para gerar e encerrar as conexões com DB a cada request HTTP """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
