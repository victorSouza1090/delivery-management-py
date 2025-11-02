import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.core.config import settings
from app.models.base import Base
from app.models.order import Order
from app.models.order_event import OrderEvent

# Configuração de logging
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Metadata usada pelo Alembic para autogeração
target_metadata = Base.metadata

# Função usada pelo Alembic no modo offline
def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Função que executa as migrations
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# Função usada pelo Alembic no modo online (Async)
async def run_migrations_online() -> None:
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Ponto de entrada do Alembic
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())