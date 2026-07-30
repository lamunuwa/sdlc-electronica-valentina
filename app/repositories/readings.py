from datetime import datetime
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.readings import ReadingInfo
from app.schemas.readings import ReadingCreate


class ReadingRepository(Protocol):
    """Define las operaciones que un repositorio debe proveer"""

    def create(
        self,
        sensor_id: int,
        reading_in: ReadingCreate,
        hash_id: str,
        timestamp: datetime | None = None,
    ) -> ReadingInfo: ...

    def by_hash(self, sensor_id: int, hash_id: str) -> bool: ...

    def get_reading(
        self,
        sensor_id: int,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReadingInfo]: ...


class ReadingSQLAlchemyRepository:
    """Crea el repositorio de lecturas en base a SQLAlchemy"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def by_hash(self, sensor_id: int, hash_id: str) -> bool:
        """Recibe sensor y hash, evalua si ya hay una lectura con esos parametros"""

        return (
            self.db.query(ReadingInfo)
            .filter(
                ReadingInfo.sensor_id == sensor_id,
                ReadingInfo.hash_id == hash_id,
            )
            .first()
            is not None
        )

    def create(
        self,
        sensor_id: int,
        reading_in: ReadingCreate,
        hash_id: str,
        timestamp: datetime | None = None,
    ) -> ReadingInfo:
        """Persiste datos de lectura y devuelve la entidad creada con su id"""

        reading = ReadingInfo(
            sensor_id=sensor_id,
            value=reading_in.value,
            unit=reading_in.unit,
            hash_id=hash_id,
        )
        if timestamp is not None:
            reading.timestamp = timestamp

        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_reading(
        self,
        sensor_id: int,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReadingInfo]:
        """Obtiene lecturas con filtros de fechas y paginacion"""

        query_filter = self.db.query(ReadingInfo).filter(ReadingInfo.sensor_id == sensor_id)
        if from_date is not None:
            query_filter = query_filter.filter(ReadingInfo.timestamp >= from_date)
        if to_date is not None:
            query_filter = query_filter.filter(ReadingInfo.timestamp <= to_date)

        query_filter = query_filter.order_by(ReadingInfo.timestamp.asc())
        return query_filter.limit(limit).offset(offset).all()
