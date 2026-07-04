from sqlalchemy import create_engine, inspect, text

from .config import settings
from .database import Base, engine
from . import models  # noqa: F401


def ensure_database() -> None:
    server_engine = create_engine(settings.database_server_url, pool_pre_ping=True, future=True)
    safe_name = settings.db_name.replace("`", "``")
    with server_engine.connect() as connection:
        connection.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{safe_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        connection.commit()
    server_engine.dispose()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def ensure_schema_updates() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "users" not in table_names:
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    with engine.connect() as connection:
        if "is_admin" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0"))
        connection.commit()


def init_database() -> None:
    ensure_database()
    create_tables()
    ensure_schema_updates()


if __name__ == "__main__":
    init_database()
    print(f"Database ready: {settings.db_name}")
