from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.readings import SQLAlchemyReadingRepository
from app.repositories.sensors import SQLAlchemyRepository
from app.schemas.readings import ReadingCreate, ReadingResponse
from app.services.catalog import SensorNotFoundError
from app.services.ingestion import DuplicateReadingError, IngestionService
from app.services.validators import SensorInactiveError, UnsupportedUnitError, ValueOutOfRangeError

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
    reading_repo = SQLAlchemyReadingRepository(db)
    sensor_repo = SQLAlchemyRepository(db)

    service = IngestionService(
        reading_repo=reading_repo,
        sensor_repo=sensor_repo,
    )

    try:
        reading = service.register_reading(sensor_id, reading_in)
        return ReadingResponse.model_validate(reading)

    except SensorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor con id {e.sensor_id} no encontrado",
        ) from e

    except UnsupportedUnitError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    except (ValueOutOfRangeError, SensorInactiveError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except DuplicateReadingError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
