from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.readings import ReadingSQLAlchemyRepository
from app.repositories.sensors import SensorSQLAlchemyRepository
from app.schemas.sensors import SensorCreate, SensorResponse, SensorStatisticsResponse, SensorUpdate
from app.services.catalog import SensorService
from app.services.validators import (
    InvalidDateRangeError,
    InvalidSensorTypeError,
    InvalidSensorUnitError,
    LimitExceededError,
    LowThreshGreaterThanHighThreshError,
    MissingRequiredFieldsError,
    NeddedChangesToUpdateSensorError,
    SensorAlreadyInactiveError,
    SensorNameDuplicateError,
    SensorNameOrIDDontMatchError,
    SensorNameTooLongError,
    SensorNoHaveReadingsError,
    SensorNotFoundError,
    SensorThresholdOutOfRangeError,
)

router = APIRouter(prefix="/sensors", tags=["SENSORS"])
dbsession = Depends(get_db)
from_date_query = Query(None, description="From")
to_date_query = Query(None, description="To")


@router.post(
    "/create",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo sensor",
)
def create_sensor(sensor_in: SensorCreate, db: Session = dbsession) -> SensorResponse:
    """Interfaz HTTP para crear un sensor"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.create_sensor(sensor_in)
        return SensorResponse.model_validate(sensor)

    except MissingRequiredFieldsError as mrfe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(mrfe)) from mrfe
    except SensorNameTooLongError as ntle:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ntle)) from ntle
    except (InvalidSensorTypeError, InvalidSensorUnitError) as ie:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ie),
        ) from ie
    except (LowThreshGreaterThanHighThreshError, SensorThresholdOutOfRangeError) as te:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(te)) from te
    except SensorNameDuplicateError as nde:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(nde),
        ) from nde


@router.get(
    "/list",
    response_model=list[SensorResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener listas de sensores",
)
def list_sensors(
    limit: int = 50,
    offset: int = 0,
    show_inactive: bool = False,
    db: Session = dbsession,
) -> list[SensorResponse]:
    """Interfaz HTTP para listar sensores"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensors = service.list_sensors(limit=limit, offset=offset, show_inactive=show_inactive)
        return [SensorResponse.model_validate(sensor) for sensor in sensors]
    except LimitExceededError as lee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(lee)) from lee


@router.get(
    "/search",
    response_model=SensorResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar un sensor por id, nombre o ambos",
)
def get_sensor(
    sensor_id: int | None = Query(None, description="Sensor ID"),
    name: str | None = Query(None, description="Sensor name"),
    db: Session = dbsession,
) -> SensorResponse:
    """Interfaz HTTP para buscar un sensor especifico"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.get_sensor(sensor_id=sensor_id, name=name)
        return SensorResponse.model_validate(sensor)
    except SensorNotFoundError as nfe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nfe)) from nfe
    except SensorNameOrIDDontMatchError as dme:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(dme)) from dme
    except MissingRequiredFieldsError as mrfe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(mrfe)) from mrfe


@router.get(
    "/statistics",
    response_model=SensorStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estadisticas de lecturas de un sensor en un periodo",
)
def get_sensor_statistics(
    sensor_id: int | None = Query(None, description="Sensor ID"),
    name: str | None = Query(None, description="Sensor name"),
    from_date: datetime | None = from_date_query,
    to_date: datetime | None = to_date_query,
    db: Session = dbsession,
) -> SensorStatisticsResponse:
    """Interfaz HTTP para obtener estadisticas de un sensor especifico"""

    sensor_repo = SensorSQLAlchemyRepository(db)
    reading_repo = ReadingSQLAlchemyRepository(db)
    service = SensorService(sensor_repo)
    try:
        return service.get_sensor_statistics(
            reading_repository=reading_repo,
            sensor_id=sensor_id,
            name=name,
            from_date=from_date,
            to_date=to_date,
        )
    except SensorNotFoundError as nfe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nfe)) from nfe
    except SensorNameOrIDDontMatchError as dme:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(dme)) from dme
    except MissingRequiredFieldsError as mrfe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(mrfe)) from mrfe
    except InvalidDateRangeError as idre:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(idre)) from idre
    except SensorNoHaveReadingsError as snhre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(snhre)) from snhre


@router.put(
    "/update",
    response_model=SensorResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un sensor",
)
def update_sensor(
    sensor_in: SensorUpdate,
    sensor_id: int | None = Query(None, description="Sensor ID"),
    name: str | None = Query(None, description="Sensor name"),
    db: Session = dbsession,
) -> SensorResponse:
    """Interfaz HTTP para actualizar un sensor"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.update_sensor(sensor_id=sensor_id, name=name, sensor_in=sensor_in)
        return SensorResponse.model_validate(sensor)
    except SensorNotFoundError as nfe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nfe)) from nfe
    except SensorNameOrIDDontMatchError as dme:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(dme)) from dme
    except MissingRequiredFieldsError as mrfe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(mrfe)) from mrfe
    except SensorNameTooLongError as ntle:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ntle)) from ntle
    except (InvalidSensorTypeError, InvalidSensorUnitError) as ie:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ie),
        ) from ie
    except (LowThreshGreaterThanHighThreshError, SensorThresholdOutOfRangeError) as te:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(te)) from te
    except SensorNameDuplicateError as de:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(de)) from de
    except NeddedChangesToUpdateSensorError as ncue:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ncue)) from ncue


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un sensor (desactivar)",
)
def delete_sensor(
    sensor_id: int | None = Query(None, description="Sensor ID"),
    name: str | None = Query(None, description="Sensor name"),
    db: Session = dbsession,
) -> None:
    """Interfaz HTTP para desactivar un sensor"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        service.deactivate_sensor(sensor_id=sensor_id, name=name)
    except SensorNotFoundError as nfe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nfe)) from nfe
    except SensorNameOrIDDontMatchError as dme:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(dme)) from dme
    except MissingRequiredFieldsError as mrfe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(mrfe)) from mrfe
    except SensorAlreadyInactiveError as aie:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(aie)) from aie
