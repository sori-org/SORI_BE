import os
import sys
from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ✅ 1. Load .env for DB connection info
load_dotenv()

database_url = os.getenv("DATABASE_URL")

# ✅ 2. Setup system path for module import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# ✅ 3. Import Base and all models to register them
from src.db.database import Base
from src.models.users import User
from src.models.accounts import Account
from src.models.stores import Store
from src.models.contents import Content
from src.models.genders import Gender
from src.models.items import Item
from src.models.ages import Age
from src.models.platforms import Platform
from src.models.formats import Format
from src.models.external_data import ExternalData


# ✅ 4. Alembic configuration
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

# ✅ 5. Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ 6. Set metadata for autogenerate
target_metadata = Base.metadata
print(f"\U0001F4CC Loaded Tables: {list(Base.metadata.tables.keys())}")

def run_migrations_offline() -> None:
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
