import asyncio
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection
from alembic import context
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from models import Base  # Import your SQLAlchemy models

# this is the Alembic Config object
config = context.config

# Get the database URL and convert asyncpg to psycopg2 for Alembic
database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgresql+asyncpg://"):
    # Convert asyncpg URL to psycopg2 URL for Alembic
    alembic_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
elif database_url and database_url.startswith("postgresql://"):
    # Already in correct format
    alembic_database_url = database_url
else:
    alembic_database_url = database_url

# Set the database URL from environment
config.set_main_option("sqlalchemy.url", alembic_database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()