from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.sensors import SensorSQLAlchemyRepository
from app.schemas.sensors import SensorCreate, SensorResponse, SensorUpdate
from app.services.catalog import SensorDuplicateError, SensorNotFoundError, SensorService

router = APIRouter(prefix="/sensors", tags=["SENSORS"])
dbsession = Depends(get_db)


@router.post(
    "",
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
    except SensorDuplicateError as d:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(d),
        ) from d


@router.get(
    "",
    response_model=list[SensorResponse],
    summary="Obtener sensores paginados",
)
def list_sensor(limit: int = 50, offset: int = 0, db: Session = dbsession) -> list[SensorResponse]:
    """Interfaz HTTP para listar sensores"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    sensors = service.list_sensors(limit=limit, offset=offset)
    return [SensorResponse.model_validate(sensor) for sensor in sensors]


@router.get(
    "/{sensor_id}",
    response_model=SensorResponse,
    summary="Obtener un sensor por id",
)
def get_sensor(sensor_id: int, db: Session = dbsession) -> SensorResponse:
    """Interfaz HTTP para buscar un sensor especifico"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.get_sensor(sensor_id)
        return SensorResponse.model_validate(sensor)
    except SensorNotFoundError as nf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nf)) from nf


@router.put(
    "/{sensor_id}",
    response_model=SensorResponse,
    summary="Actualizar un sensor",
)
def update_sensor(
    sensor_id: int, sensor_in: SensorUpdate, db: Session = dbsession
) -> SensorResponse:
    """Interfaz HTTP para actualizar un sensor"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        sensor = service.update_sensor(sensor_id, sensor_in)
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
    """Interfaz HTTP para desactivar un sensor"""

    repo = SensorSQLAlchemyRepository(db)
    service = SensorService(repo)
    try:
        service.deactivate_sensor(sensor_id)
    except SensorNotFoundError as nf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(nf)) from nf
