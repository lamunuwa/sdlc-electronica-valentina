from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alerts import AlertInfo


class AlertRepository:
    """Persiste y consulta alertas"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_alert(self, alert_data: dict) -> AlertInfo:
        alert = AlertInfo(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_all_alerts(
        self, from_date: datetime | None, to_date: datetime | None, limit: int, offset: int
    ) -> list[AlertInfo]:
        statement = select(AlertInfo)
        if from_date:
            statement = statement.where(AlertInfo.timestamp >= from_date)
        if to_date:
            statement = statement.where(AlertInfo.timestamp <= to_date)
        statement = (
            statement.order_by(AlertInfo.timestamp.desc(), AlertInfo.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_alerts_by_sensor(
        self,
        sensor_id: int,
        from_date: datetime | None,
        to_date: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AlertInfo]:
        statement = select(AlertInfo).where(AlertInfo.sensor_id == sensor_id)
        if from_date:
            statement = statement.where(AlertInfo.timestamp >= from_date)
        if to_date:
            statement = statement.where(AlertInfo.timestamp <= to_date)
        statement = (
            statement.order_by(AlertInfo.timestamp.desc(), AlertInfo.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def get_by_id(self, alert_id: int) -> AlertInfo | None:
        return self.db.get(AlertInfo, alert_id)

    def update_alert(self, alert: AlertInfo) -> AlertInfo:
        self.db.commit()
        self.db.refresh(alert)
        return alert
