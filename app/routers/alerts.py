from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.alerts import AlertRepository
from app.schemas.alerts import AlertResponse
from app.services.anomalies import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])
dbsession = Depends(get_db)
from_date_query = Query(None, alias="from")
to_date_query = Query(None, alias="to")


@router.get(
    "",
    response_model=list[AlertResponse],
    summary="Listar alertas por sensor",
)
def list_alerts(
    sensor_id: int,
    from_date: datetime | None = from_date_query,
    to_date: datetime | None = to_date_query,
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = dbsession,
) -> list[AlertResponse]:
    """Obtiene alertas de un sensor"""
    service = AlertService(AlertRepository(db))
    alerts = service.get_alerts(sensor_id, from_date, to_date, limit, offset)
    return [AlertResponse.model_validate(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse, summary="Obtener alerta por id")
def get_alert(alert_id: int, db: Session = dbsession) -> AlertResponse:
    """Obtiene una alerta por su id"""
    alert = AlertService(AlertRepository(db)).get_alert(alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")
    return AlertResponse.model_validate(alert)
