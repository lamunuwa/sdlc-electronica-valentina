from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.sensors import SQLAlchemyRepository
from app.schemas.sensors import SensorCreate, SensorResponse
from app.services.catalog import SensorDuplicateError, SensorService

router = APIRouter(prefix="/sensors", tags=["sensors"])
dbsession = Depends(get_db)


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo sensor",
)
def create_sensor(sensor_in: SensorCreate, db: Session = dbsession) -> SensorResponse:
    repo = SQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.create_sensor(sensor_in)
        return SensorResponse.model_validate(sensor)
    except SensorDuplicateError as d:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(d),
        ) from d
