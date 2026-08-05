import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def get_database_url() -> str:
    """Cambia la URL de la DB para que sea compatible con diferentes entornos"""

    url = os.getenv("DATABASE_URL", "sqlite:///sensorhub.db")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


db_url = get_database_url()

engine = create_engine(db_url)
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase): ...


def get_db() -> Generator[Session]:
    """Abre la DB para el ingreso y luego la cierra"""

    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
