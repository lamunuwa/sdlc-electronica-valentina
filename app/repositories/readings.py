from datetime import datetime
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.readings import ReadingInfo
from app.schemas.readings import ReadingCreate


class RepositoryProtocolReading(Protocol):
    def create(
        self,
        sensor_id: int,
        reading_in: ReadingCreate,
        hash_id: str,
        timestamp: datetime | None = None,
    ) -> ReadingInfo: ...

    def exists_by_hash(self, sensor_id: int, hash_id: str) -> bool: ...


class SQLAlchemyReadingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def exists_by_hash(self, sensor_id: int, hash_id: str) -> bool:
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
