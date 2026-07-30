from typing import Protocol

from sqlalchemy.orm import Session

from app.models.sensors import SensorInfo
from app.schemas.sensors import SensorCreate, SensorUpdate


class SensorRepository(Protocol):
    """Define las operaciones que un repositorio debe proveer"""

    def by_name(self, name: str) -> SensorInfo | None: ...

    def create(self, sensor_in: SensorCreate) -> SensorInfo: ...

    def list_all(self) -> list[SensorInfo]: ...

    def by_id(self, sensor_id: int) -> SensorInfo | None: ...

    def update(self, sensor: SensorInfo, sensor_in: SensorUpdate) -> SensorInfo: ...

    def deactivate(self, sensor: SensorInfo) -> SensorInfo: ...


class SensorSQLAlchemyRepository:
    """Crea el repositorio de sensores en base a SQLAlchemy"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def by_name(self, name: str) -> SensorInfo | None:
        """Entrega el sensor coincidente o "None" en base a un sensor buscado"""

        return self.db.query(SensorInfo).filter(SensorInfo.name == name).first()

    def create(self, sensor_in: SensorCreate) -> SensorInfo:
        """Crea una entidad (sensor) con los datos validados"""

        db_sensor = SensorInfo(**sensor_in.model_dump())
        self.db.add(db_sensor)
        self.db.commit()
        self.db.refresh(db_sensor)
        return db_sensor

    def list_all(self) -> list[SensorInfo]:
        """Lista todos los sensores existentes"""

        return self.db.query(SensorInfo).all()

    def by_id(self, sensor_id: int) -> SensorInfo | None:
        """En base a un ID busca una coincidencia, si no hay devuelve "None" """

        return self.db.query(SensorInfo).filter(SensorInfo.id == sensor_id).first()

    def update(self, sensor: SensorInfo, sensor_in: SensorUpdate) -> SensorInfo:
        """Cambia informacion en base a un ID de un sensor y lo guarda"""

        changes = sensor_in.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(sensor, field, value)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def deactivate(self, sensor: SensorInfo) -> SensorInfo:
        """Desactiva sensores"""

        sensor.active = False
        self.db.commit()
        self.db.refresh(sensor)
        return sensor


# Clases de apoyo ---------------------------------------
""" Mantiene historicos en lo que se hacen cambios """


class RepositoryProtocol(SensorRepository, Protocol):
    def desactivate(self, sensor: SensorInfo) -> SensorInfo: ...


class SQLAlchemyRepository(SensorSQLAlchemyRepository):
    def desactivate(self, sensor: SensorInfo) -> SensorInfo:
        return self.deactivate(sensor)  # pragma: no cover


# -------------------------------------------------------
