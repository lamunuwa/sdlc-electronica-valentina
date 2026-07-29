from typing import Protocol

from sqlalchemy.orm import Session

from app.models.sensors import SensorInfo
from app.schemas.sensors import SensorCreate, SensorUpdate


class RepositoryProtocol(Protocol):
    """Protocolo para uso del repositorio"""

    def by_name(self, name: str) -> SensorInfo | None: ...

    def create(self, sensor_in: SensorCreate) -> SensorInfo: ...

    def list_all(self) -> list[SensorInfo]: ...

    def by_id(self, sensor_id: int) -> SensorInfo | None: ...

    def update(self, sensor_id: SensorInfo, sensor_in: SensorUpdate) -> SensorInfo | None: ...

    def desactivate(self, sensor: SensorInfo) -> SensorInfo | None: ...


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

    def list_all(self) -> list[SensorInfo]:
        return self.db.query(SensorInfo).all()

    def by_id(self, sensor_id: int) -> SensorInfo | None:
        return self.db.query(SensorInfo).filter(SensorInfo.id == sensor_id).first()

    def update(self, sensor_id: SensorInfo, sensor_in: SensorUpdate) -> SensorInfo:
        update = sensor_in.model_dump(exclude_unset=True)
        for f, v in update.items():  # Field (f) y Value (v)
            setattr(sensor_id, f, v)
        self.db.commit()
        self.db.refresh(sensor_id)
        return sensor_id

    def desactivate(self, sensor_id: SensorInfo) -> SensorInfo:
        sensor_id.active = False
        self.db.commit()
        self.db.refresh(sensor_id)
        return sensor_id
