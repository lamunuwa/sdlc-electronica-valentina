from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alerts import AlertInfo


class AlertRepository(Protocol):
    """Define las operaciones que un repositorio debe proveer"""

    def create_alert(self, alert_data: dict) -> AlertInfo: ...

    def get_all_alerts(
        self, from_date: datetime | None, to_date: datetime | None, limit: int, offset: int
    ) -> list[AlertInfo]: ...

    def get_alerts_by_sensor(
        self,
        sensor_id: int,
        from_date: datetime | None,
        to_date: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AlertInfo]: ...

    def get_by_id(self, alert_id: int) -> AlertInfo | None: ...

    def update_alert(self, alert: AlertInfo) -> AlertInfo: ...


class AlertSQLAlchemyRepository:
    """Crea el repositorio de alertas en base a SQLAlchemy"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_alert(self, alert_data: dict) -> AlertInfo:
        """Crea una nueva alerta en la base de datos"""
        alert = AlertInfo(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_all_alerts(
        self, from_date: datetime | None, to_date: datetime | None, limit: int, offset: int
    ) -> list[AlertInfo]:
        """Obtiene todas las alertas registradas en la base de datos"""
        sen = select(AlertInfo)
        if from_date:
            sen = sen.where(AlertInfo.timestamp >= from_date)
        if to_date:
            sen = sen.where(AlertInfo.timestamp <= to_date)
        sen = (
            sen.order_by(AlertInfo.timestamp.desc(), AlertInfo.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(sen).all())

    def get_alerts_by_sensor(
        self,
        sensor_id: int,
        from_date: datetime | None,
        to_date: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AlertInfo]:
        """Obtiene las alertas registradas en la base de datos de un sensor"""
        sen = select(AlertInfo).where(AlertInfo.sensor_id == sensor_id)
        if from_date:
            sen = sen.where(AlertInfo.timestamp >= from_date)
        if to_date:
            sen = sen.where(AlertInfo.timestamp <= to_date)
        sen = (
            sen.order_by(AlertInfo.timestamp.desc(), AlertInfo.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(sen).all())

    def get_by_id(self, alert_id: int) -> AlertInfo | None:
        """Obtiene una alerta registrada en la base de datos por su ID"""
        return self.db.get(AlertInfo, alert_id)

    def update_alert(self, alert: AlertInfo) -> AlertInfo:
        """Actualiza una alerta registrada en la base de datos"""
        self.db.commit()
        self.db.refresh(alert)
        return alert
