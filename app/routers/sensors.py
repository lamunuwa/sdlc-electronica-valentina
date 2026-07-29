from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.sensors import SQLAlchemyRepository
from app.schemas.sensors import SensorCreate, SensorResponse, SensorUpdate
from app.services.catalog import SensorDuplicateError, SensorNotFoundError, SensorService

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
        sensor = service.create_sensors(sensor_in)
        return SensorResponse.model_validate(sensor)
    except SensorDuplicateError as d:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(d),
        ) from d


@router.get(
    "",
    response_model=list[SensorResponse],
    summary="Obtener todos los sensores",
)
def list_sensor(db: Session = dbsession) -> list[SensorResponse]:
    repo = SQLAlchemyRepository(db)
    service = SensorService(repo)
    sensors = service.list_sensors()
    return [SensorResponse.model_validate(sensor) for sensor in sensors]


@router.get(
    "/{sensor_id}",
    response_model=SensorResponse,
    summary="Obtener un sensor por id",
)
def get_sensor(sensor_id: int, db: Session = dbsession) -> SensorResponse:
    repo = SQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.get_sensors(sensor_id)
        return SensorResponse.model_validate(sensor)
    except SensorNotFoundError as nf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nf)) from nf


@router.patch(
    "/{sensor_id}",
    response_model=SensorResponse,
    summary="Actualizar un sensor",
)
def update_sensor(
    sensor_id: int, sensor_in: SensorUpdate, db: Session = dbsession
) -> SensorResponse:
    repo = SQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.update_sensors(sensor_id, sensor_in)
        return SensorResponse.model_validate(sensor)
    except SensorNotFoundError as nf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nf)) from nf
    except SensorDuplicateError as d:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(d)) from d


@router.delete(
    "/{sensor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un sensor (desactivar)",
)
def delete_sensor(sensor_id: int, db: Session = dbsession) -> None:
    repo = SQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        service.desactivate_sensors(sensor_id)
    except SensorNotFoundError as nf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nf)) from nf
