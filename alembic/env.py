import contextlib
import os
from logging.config import fileConfig
from pathlib import Path

from alembic.config import Config
from alembic.script import write_hooks
from sqlalchemy import engine_from_config, pool, text

import app.schemas.schemas  # noqa
from alembic import context, command
from app.core.config import ApiConfig
from app.database.database import Base

# print(Base.metadata.tables)
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
config.set_section_option(section, "DB_PG_URL", ApiConfig().DB_PG_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    schema = context.get_x_argument(as_dictionary=True).get("schema", None)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        if schema:
            connection.execute(text('set session search_path to "%s"' % schema))
            connection.dialect.default_schema_name = schema

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


@write_hooks.register("sql_migration")
def gen_sql_migrations(filename, _options):
    # Triggers, functions (or whatever that needs tables created)
    # has to be registered here.

    create_dir_if_not()

    new_revision, down_revision = get_revisions(filename)

    sql_filename = filename.split("/")[-1][:-3]
    if not new_revision:
        return

    ini_file_path = Path(__file__).parent.parent / "alembic.ini"
    migrations_dir = Path(__file__).parent.parent / "migrations"
    sql_version_upgrade_path = migrations_dir / "upgrade" / f"{sql_filename}.sql"
    sql_version_downgrade_path = migrations_dir / "downgrade" / f"{sql_filename}.sql"

    alembic_cfg = Config(ini_file_path)
    alembic_cfg.set_main_option("script_location", "alembic")

    # Generates upgrade sql
    with open(sql_version_upgrade_path, "w") as f:
        with contextlib.redirect_stdout(f):
            revision_str = (
                f"{down_revision}:{new_revision}" if down_revision else "head"
            )
            command.upgrade(alembic_cfg, revision_str, sql=True)

    # Generated downgrade sql
    # While downgrading, we must have to specify the range
    if new_revision and down_revision:
        with open(sql_version_downgrade_path, "w") as f:
            with contextlib.redirect_stdout(f):
                revision_str = (
                    f"{new_revision}:{down_revision}"
                    if down_revision
                    else f"{new_revision}:-1"
                )
                command.downgrade(alembic_cfg, revision_str, sql=True)

    elif new_revision:
        # This should only happen for first revision
        with open(sql_version_downgrade_path, "w") as f:
            f.write("--- If this is first downgrade revision, it will be empty. Manually added the downgrade SQL.")


def get_revisions(file_path):
    # Initialize an empty dictionary to store the variables
    variables = {}

    try:
        # Open the file in read mode
        with open(file_path) as f:
            # Read the contents of the file
            file_contents = f.read()

            # Execute the code in the file's context
            exec(file_contents, variables)

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error while reading variables: {e}")

    return variables.get("revision"), variables.get("down_revision")


def create_dir_if_not():
    migrations_path = Path(__file__).parent.parent / "migrations"
    if not os.path.exists(str(migrations_path)):
        os.makedirs(migrations_path)

    upgrade_path = migrations_path / "upgrade"
    if not os.path.exists(str(upgrade_path)):
        os.makedirs(upgrade_path)

    downgrade_path = migrations_path / "downgrade"
    if not os.path.exists(str(downgrade_path)):
        os.makedirs(downgrade_path)
