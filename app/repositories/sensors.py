from typing import Protocol

from sqlalchemy.orm import Session

from app.models.sensors import SensorInfo
from app.schemas.sensors import SensorCreate


class RepositoryProtocol(Protocol):
    """Protocolo para uso del repositorio"""

    def by_name(self, name: str) -> SensorInfo | None: ...

    def create(self, sensor_in: SensorCreate) -> SensorInfo: ...


class SQLAlchemyRepository:
    """Clase para la base de datos"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def by_name(self, name: str) -> SensorInfo | None:
        return self.db.query(SensorInfo).filter(SensorInfo.name == name).first()

    def create(self, sensor_in: SensorCreate) -> SensorInfo:
        db_sensor = SensorInfo(**sensor_in.model_dump())
        self.db.add(db_sensor)
        self.db.commit()
        self.db.refresh(db_sensor)
        return db_sensor
