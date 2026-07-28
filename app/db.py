from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

db_url = "sqlite:///./sensorhub.db"

engine = create_engine(db_url, connect_args={"check_same_thread": False})
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Clase para crear modelos de la base de datos"""

    ...


def get_db() -> Generator[Session]:
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
