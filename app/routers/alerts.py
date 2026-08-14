from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.alerts import AlertSQLAlchemyRepository
from app.repositories.sensors import SensorSQLAlchemyRepository
from app.schemas.alerts import AlertResponse, AlertStateUpdate
from app.services.anomalies import AlertService
from app.services.validators import (
    AlertNotFoundError,
    InvalidAlertStatusError,
    InvalidDateRangeError,
    MissingAlertStatusError,
    MissingRequiredFieldsError,
    NeededChangesToUpdateAlertError,
    SensorNameOrIDDontMatchError,
    SensorNotFoundError,
)

router = APIRouter(prefix="/alerts", tags=["Alerts"])
dbsession = Depends(get_db)
from_date_query = Query(None, description="From")
to_date_query = Query(None, description="To")


@router.get(
    "/list",
    response_model=list[AlertResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todas las alertas",
)
def list_alerts(
    from_date: datetime | None = from_date_query,
    to_date: datetime | None = to_date_query,
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = dbsession,
) -> list[AlertResponse]:
    """Interfaz HTTP para listar todas las alertas con filtros opcionales"""

    alert_repo = AlertSQLAlchemyRepository(db)
    service = AlertService(alert_repo)

    try:
        alerts = service.get_all_alerts(from_date, to_date, limit, offset)
        return [AlertResponse.model_validate(alert) for alert in alerts]
    except InvalidDateRangeError as idre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(idre),
        ) from idre


@router.get(
    "/search",
    response_model=list[AlertResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener alertas por sensor",
)
def get_alerts_by_sensor(
    sensor_id: int | None = Query(None, description="Sensor ID"),
    name: str | None = Query(None, description="Sensor name"),
    from_date: datetime | None = from_date_query,
    to_date: datetime | None = to_date_query,
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = dbsession,
) -> list[AlertResponse]:
    """Interfaz HTTP para obtener alertas de un sensor específico"""

    alert_repo = AlertSQLAlchemyRepository(db)
    sensor_repo = SensorSQLAlchemyRepository(db)
    service = AlertService(alert_repo, sensor_repo)

    try:
        alerts = service.get_alerts_by_sensor(
            sensor_id=sensor_id,
            name=name,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )
        return [AlertResponse.model_validate(alert) for alert in alerts]
    except MissingRequiredFieldsError as mrfe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(mrfe),
        ) from mrfe
    except SensorNotFoundError as snfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(snfe),
        ) from snfe
    except SensorNameOrIDDontMatchError as dme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(dme),
        ) from dme
    except InvalidDateRangeError as idre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(idre),
        ) from idre


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener alerta por id",
)
def get_alert(alert_id: int, db: Session = dbsession) -> AlertResponse:
    """Interfaz HTTP para obtener una alerta por su id"""

    alert_repo = AlertSQLAlchemyRepository(db)
    service = AlertService(alert_repo)

    try:
        alert = service.get_alert(alert_id)
        return AlertResponse.model_validate(alert)
    except AlertNotFoundError as anfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(anfe),
        ) from anfe


@router.put(
    "/{alert_id}",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado de una alerta",
)
def update_alert(
    alert_id: int,
    alert_in: AlertStateUpdate,
    db: Session = dbsession,
) -> AlertResponse:
    """Interfaz HTTP para actualizar el estado de una alerta"""

    alert_repo = AlertSQLAlchemyRepository(db)
    service = AlertService(alert_repo)

    try:
        alert = service.update_alert_state(alert_id, alert_in.state)
        return AlertResponse.model_validate(alert)
    except MissingAlertStatusError as mase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(mase),
        ) from mase
    except InvalidAlertStatusError as iase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(iase),
        ) from iase
    except AlertNotFoundError as anfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(anfe),
        ) from anfe
    except NeededChangesToUpdateAlertError as ncae:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ncae),
        ) from ncae
