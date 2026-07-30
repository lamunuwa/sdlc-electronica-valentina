from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

db_url = "sqlite:///./sensorhub.db"

engine = create_engine(db_url, connect_args={"check_same_thread": False})
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase): ...


def get_db() -> Generator[Session]:
    """Abre la DB para el ingreso y luego la cierra"""

    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
