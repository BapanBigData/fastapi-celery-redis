from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from src.app.utils.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(url=Config.DATABASE_URL, echo=True)


async def init_db():
    async with engine.begin() as conn:
        from src.app.models.models import Book  # noqa: F401

        # `conn.run_sync()` runs a synchronous function (like `create_all`) inside the `async` engine’s threadpool,
        # so it returns an awaitable that must be awaited.

        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:

    Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        yield session
