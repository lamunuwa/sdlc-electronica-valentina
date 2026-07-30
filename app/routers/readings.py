from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.readings import ReadingSQLAlchemyRepository
from app.repositories.sensors import SensorSQLAlchemyRepository
from app.schemas.readings import ReadingCreate, ReadingResponse
from app.services.catalog import SensorNotFoundError
from app.services.ingestion import DuplicateReadingError, ReadingService
from app.services.validators import (
    SensorInactiveError,
    UnsupportedUnitError,
    ValueOutOfRangeError,
)

router = APIRouter(prefix="/sensors", tags=["readings"])
dbsession = Depends(get_db)


@router.post(
    "/{sensor_id}/readings",
    response_model=ReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva lectura para un sensor",
)
def create_reading(
    sensor_id: int,
    reading_in: ReadingCreate,
    db: Session = dbsession,
) -> ReadingResponse:
    """Interfaz HTTP para registrar una lectura"""

    reading_repo = ReadingSQLAlchemyRepository(db)
    sensor_repo = SensorSQLAlchemyRepository(db)
    service = ReadingService(reading_repository=reading_repo, sensor_repository=sensor_repo)

    try:
        reading = service.register_reading(sensor_id, reading_in)
        return ReadingResponse.model_validate(reading)

    except SensorNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor con id {error.sensor_id} no encontrado",
        ) from error

    except UnsupportedUnitError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    except (ValueOutOfRangeError, SensorInactiveError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except DuplicateReadingError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
