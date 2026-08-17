from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.alerts import AlertSQLAlchemyRepository
from app.repositories.readings import ReadingSQLAlchemyRepository
from app.repositories.sensors import SensorSQLAlchemyRepository
from app.schemas.readings import ReadingCreate, ReadingResponse
from app.services.anomalies import AlertService
from app.services.ingestion import ReadingService
from app.services.validators import (
    DuplicateReadingError,
    InvalidDateRangeError,
    LimitExceededError,
    MissingRequiredFieldsError,
    SensorCantProcessUnitError,
    SensorInactiveError,
    SensorNameOrIDDontMatchError,
    SensorNotFoundError,
    TimestampInFutureError,
)

router = APIRouter(prefix="/readings", tags=["READINGS"])
dbsession = Depends(get_db)
from_date_query = Query(None, description="From")
to_date_query = Query(None, description="To")


@router.post(
    "/{sensor_id}",
    response_model=ReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva lectura",
)
def create_reading(
    sensor_id: int,
    reading_in: ReadingCreate,
    db: Session = dbsession,
) -> ReadingResponse:
    """Interfaz HTTP para registrar una lectura. Solo se registra por sensor_id (path)"""

    reading_repo = ReadingSQLAlchemyRepository(db)
    sensor_repo = SensorSQLAlchemyRepository(db)
    alert_repo = AlertSQLAlchemyRepository(db)

    service = ReadingService(sensor_repository=sensor_repo, reading_repository=reading_repo)
    alert_service = AlertService(alert_repo, sensor_repo)

    try:
        reading = service.register_reading(sensor_id, reading_in)
        alert_service.process_reading(reading)
        return ReadingResponse.model_validate(reading)

    except SensorNotFoundError as nfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(nfe),
        ) from nfe
    except SensorInactiveError as sie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(sie),
        ) from sie
    except SensorCantProcessUnitError as cpe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(cpe),
        ) from cpe
    except TimestampInFutureError as tfe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(tfe),
        ) from tfe
    except DuplicateReadingError as dre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(dre),
        ) from dre


@router.get(
    "/search",
    response_model=list[ReadingResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar lecturas",
)
def get_readings(
    sensor_id: int | None = Query(None, description="Sensor ID"),
    name: str | None = Query(None, description="Sensor name"),
    from_date: datetime | None = from_date_query,
    to_date: datetime | None = to_date_query,
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = dbsession,
) -> list[ReadingResponse]:
    """Interfaz HTTP para consultar lecturas, buscando el sensor igual que en sensors"""

    reading_repo = ReadingSQLAlchemyRepository(db)
    sensor_repo = SensorSQLAlchemyRepository(db)
    service = ReadingService(reading_repository=reading_repo, sensor_repository=sensor_repo)

    try:
        readings = service.get_readings(
            sensor_id=sensor_id,
            name=name,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )
    except MissingRequiredFieldsError as mrfe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(mrfe),
        ) from mrfe
    except SensorNotFoundError as nfe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(nfe),
        ) from nfe
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
    except LimitExceededError as lee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(lee)) from lee

    return [ReadingResponse.model_validate(rr) for rr in readings]
