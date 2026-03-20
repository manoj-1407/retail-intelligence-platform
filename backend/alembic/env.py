
from __future__ import annotations
import os, sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("[FATAL] DATABASE_URL env var not set", file=sys.stderr)
    sys.exit(1)

config.set_main_option("sqlalchemy.url", db_url)
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline():
    context.configure(url=db_url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    conn = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", poolclass=pool.NullPool,
    )
    with conn.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
