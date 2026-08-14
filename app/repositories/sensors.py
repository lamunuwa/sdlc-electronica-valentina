from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sensors import SensorInfo
from app.schemas.sensors import SensorCreate, SensorUpdate


class SensorRepository(Protocol):
    """Define las operaciones que un repositorio debe proveer"""

    def by_name(self, name: str) -> SensorInfo | None: ...

    def create(self, sensor_in: SensorCreate) -> SensorInfo: ...

    def list_sensor(
        self, limit: int = 50, offset: int = 0, show_inactive: bool = False
    ) -> list[SensorInfo]: ...

    def by_id(self, sensor_id: int) -> SensorInfo | None: ...

    def update(self, sensor: SensorInfo, sensor_in: SensorUpdate) -> SensorInfo: ...

    def deactivate(self, sensor: SensorInfo) -> SensorInfo: ...


class SensorSQLAlchemyRepository:
    """Crea el repositorio de sensores en base a SQLAlchemy"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def by_name(self, name: str) -> SensorInfo | None:
        """Entrega el sensor coincidente o "None" en base a un sensor buscado"""

        sen = select(SensorInfo).where(SensorInfo.name == name)
        return self.db.scalars(sen).first()

    def create(self, sensor_in: SensorCreate) -> SensorInfo:
        """Crea una entidad (sensor) con los datos validados"""

        sensor_data = sensor_in.model_dump(exclude={"sensor_umbral"})
        threshold_data = sensor_in.sensor_umbral
        db_sensor = SensorInfo(
            **sensor_data,
            threshold_min=threshold_data.min,
            threshold_max=threshold_data.max,
        )
        self.db.add(db_sensor)
        self.db.commit()
        self.db.refresh(db_sensor)
        return db_sensor

    def list_sensor(
        self, limit: int = 50, offset: int = 0, show_inactive: bool = False
    ) -> list[SensorInfo]:
        """Lista sensores paginados"""

        sen = select(SensorInfo)
        if not show_inactive:
            sen = sen.where(SensorInfo.active.is_(True))

        sen = sen.order_by(SensorInfo.id.asc()).offset(offset).limit(limit)
        return list(self.db.scalars(sen).all())

    def by_id(self, sensor_id: int) -> SensorInfo | None:
        """En base a un ID busca una coincidencia, si no hay devuelve "None" """

        return self.db.get(SensorInfo, sensor_id)

    def update(self, sensor: SensorInfo, sensor_in: SensorUpdate) -> SensorInfo:
        """Cambia informacion en base a un ID de un sensor y lo guarda"""

        changes = sensor_in.model_dump(exclude_unset=True)
        threshold_data = changes.pop("sensor_umbral", None)
        if threshold_data is not None:
            if threshold_data.get("min") is not None:
                changes["threshold_min"] = threshold_data["min"]
            if threshold_data.get("max") is not None:
                changes["threshold_max"] = threshold_data["max"]

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
    def deactivate(self, sensor: SensorInfo) -> SensorInfo: ...


class SQLAlchemyRepository(SensorSQLAlchemyRepository):
    def deactivate(self, sensor: SensorInfo) -> SensorInfo:
        return self.deactivate(sensor)  # pragma: no cover


# -------------------------------------------------------
