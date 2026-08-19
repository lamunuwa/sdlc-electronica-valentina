from datetime import datetime
from typing import Protocol

from sqlalchemy import func, select
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
        sensor_id: int | None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReadingInfo]: ...

    def get_statistics(
        self,
        sensor_id: int | None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> tuple[int, float | None, float | None, float | None]: ...


class ReadingSQLAlchemyRepository:
    """Crea el repositorio de lecturas en base a SQLAlchemy"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def by_hash(self, sensor_id: int, hash_id: str) -> bool:
        """Recibe sensor y hash, evalua si ya hay una lectura con esos parametros"""

        sen = select(ReadingInfo).where(
            ReadingInfo.sensor_id == sensor_id,
            ReadingInfo.hash_id == hash_id,
        )
        return self.db.execute(sen).first() is not None

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
        effective_timestamp = reading_in.timestamp or timestamp
        if effective_timestamp is not None:
            reading.timestamp = effective_timestamp

        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_reading(
        self,
        sensor_id: int | None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ReadingInfo]:
        """Obtiene lecturas con filtros de fechas y paginacion"""

        sen = select(ReadingInfo)
        if sensor_id is not None:
            sen = sen.where(ReadingInfo.sensor_id == sensor_id)

        if from_date is not None:
            sen = sen.where(ReadingInfo.timestamp >= from_date)
        if to_date is not None:
            sen = sen.where(ReadingInfo.timestamp <= to_date)

        sen = sen.order_by(
            ReadingInfo.timestamp.asc(),
            ReadingInfo.id.asc(),
        )

        if offset is not None:
            sen = sen.offset(offset)
        if limit is not None:
            sen = sen.limit(limit)

        return list(self.db.scalars(sen).all())

    def get_statistics(
        self,
        sensor_id: int | None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> tuple[int, float | None, float | None, float | None]:
        """Calcula total, minimo, maximo y promedio de lecturas para un sensor y periodo"""

        sen = select(
            func.count(ReadingInfo.id),
            func.min(ReadingInfo.value),
            func.max(ReadingInfo.value),
            func.avg(ReadingInfo.value),
        ).where(ReadingInfo.sensor_id == sensor_id)

        if from_date is not None:
            sen = sen.where(ReadingInfo.timestamp >= from_date)
        if to_date is not None:
            sen = sen.where(ReadingInfo.timestamp <= to_date)

        total, min_value, max_value, avg_value = self.db.execute(sen).one()
        return total, min_value, max_value, avg_value
