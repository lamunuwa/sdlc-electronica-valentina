from app.core.limits import is_type_supported, is_unit_supported
from app.models.sensors import SensorInfo
from app.repositories.sensors import SensorRepository
from app.schemas.sensors import SensorCreate, SensorUpdate
from app.services.validators import (
    EmptySensorThresholdError,
    InvalidSensorTypeError,
    InvalidSensorUnitError,
    SensorDuplicateError,
    SensorNotFoundError,
)


class SensorService:
    """Todas las sesiones de consulta y modificacion del catalogo de sensores"""

    def __init__(self, repository: SensorRepository) -> None:
        self.repository = repository

    # funciones de apoyo ---------------------------------------
    def validate_sensor_configuration(self, sensor_type: str, unit: str) -> None:
        """Valida que el tipo y la unidad sean compatibles con las reglas del sistema"""
        if not is_type_supported(sensor_type):
            raise InvalidSensorTypeError(sensor_type)
        if not is_unit_supported(sensor_type, unit):
            raise InvalidSensorUnitError(sensor_type, unit)

    # ----------------------------------------------------------

    def create_sensor(self, sensor_in: SensorCreate) -> SensorInfo:
        """Crea un nuevo sensor validando duplicidad"""
        self.validate_sensor_configuration(sensor_in.type, sensor_in.unit)
        threshold = sensor_in.sensor_umbral
        if threshold.min is None or threshold.max is None:
            raise EmptySensorThresholdError()
        if self.repository.by_name(sensor_in.name):
            raise SensorDuplicateError(sensor_in.name)
        return self.repository.create(sensor_in)

    def list_sensors(self, limit: int = 50, offset: int = 0) -> list[SensorInfo]:
        """Obtiene y devuelve la lista de sensores paginados"""
        return self.repository.list_sensor(limit=limit, offset=offset)

    def get_sensor(self, sensor_id: int) -> SensorInfo:
        """Busca un sensor por su ID. Lanza SensorNotFoundError si no existe"""
        sensor = self.repository.by_id(sensor_id)
        if sensor is None:
            raise SensorNotFoundError(sensor_id)
        return sensor

    def update_sensor(self, sensor_id: int, sensor_in: SensorUpdate) -> SensorInfo:
        """Actualiza la información de un sensor. No debe existir ya"""
        sensor = self.get_sensor(sensor_id)
        new_name = sensor_in.name
        if new_name is not None and new_name != sensor.name and self.repository.by_name(new_name):
            raise SensorDuplicateError(new_name)

        sensor_type = sensor_in.type if sensor_in.type is not None else sensor.type
        sensor_unit = sensor_in.unit if sensor_in.unit is not None else sensor.unit
        self.validate_sensor_configuration(sensor_type, sensor_unit)
        return self.repository.update(sensor, sensor_in)

    def deactivate_sensor(self, sensor_id: int) -> SensorInfo:
        """Desactiva un sensor (marca inactivo)"""
        return self.repository.deactivate(self.get_sensor(sensor_id))
