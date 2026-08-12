from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alerts import AlertInfo


class AlertRepository:
    """Persiste y consulta alertas"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, alert_data: dict[str, int | str | float | datetime]) -> AlertInfo:
        """Crea una alerta y devuelve la entidad persistida"""
        alert = AlertInfo(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_by_sensor_id(self, sensor_id: int) -> list[AlertInfo]:
        """Lista alertas filtradas y paginadas por sensor"""
        statement = select(AlertInfo).where(AlertInfo.sensor_id == sensor_id)
        return list(self.db.scalars(statement.order_by(AlertInfo.timestamp.desc())).all())

    def get_alerts(
        self,
        sensor_id: int,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AlertInfo]:
        """Obtiene alertas de un sensor"""
        statement = select(AlertInfo).where(AlertInfo.sensor_id == sensor_id)
        if from_date is not None:
            statement = statement.where(AlertInfo.timestamp >= from_date)
        if to_date is not None:
            statement = statement.where(AlertInfo.timestamp <= to_date)
        statement = statement.order_by(AlertInfo.timestamp.desc(), AlertInfo.id.desc())
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.db.scalars(statement).all())

    def get_by_id(self, alert_id: int) -> AlertInfo | None:
        """Obtiene una alerta por su id"""
        return self.db.get(AlertInfo, alert_id)
