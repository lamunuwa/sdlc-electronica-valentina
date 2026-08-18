from app.core.limits import is_type_supported, is_unit_supported, is_value_valid
from app.models.sensors import SensorInfo
from app.repositories.sensors import SensorRepository
from app.schemas.sensors import SensorCreate, SensorUpdate
from app.services.validators import (
    InvalidSensorTypeError,
    InvalidSensorUnitError,
    LimitExceededError,
    LowThreshGreaterThanHighThreshError,
    MissingRequiredFieldsError,
    NeddedChangesToUpdateSensorError,
    SensorAlreadyInactiveError,
    SensorNameDuplicateError,
    SensorNameTooLongError,
    SensorThresholdOutOfRangeError,
    ValidateSensorParameters,
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

    def validate_sensor_threshold(
        self, sensor_type: str, unit: str, min_value: float, max_value: float
    ) -> None:
        """Valida que los umbrales min y max sean consistentes y dentro del rango fisico"""
        if min_value > max_value:
            raise LowThreshGreaterThanHighThreshError
        if not is_value_valid(sensor_type, unit, min_value) or not is_value_valid(
            sensor_type, unit, max_value
        ):
            raise SensorThresholdOutOfRangeError(unit)

    # ----------------------------------------------------------

    def create_sensor(self, sensor_in: SensorCreate) -> SensorInfo:
        """Crea un nuevo sensor validando duplicidad"""
        if len(sensor_in.name) > 30:
            raise SensorNameTooLongError(sensor_in.name)

        if self.repository.by_name(sensor_in.name) is not None:
            raise SensorNameDuplicateError(sensor_in.name)

        self.validate_sensor_configuration(sensor_in.type, sensor_in.unit)

        threshold = sensor_in.sensor_umbral
        if not threshold or threshold.min is None or threshold.max is None:
            raise MissingRequiredFieldsError

        self.validate_sensor_threshold(sensor_in.type, sensor_in.unit, threshold.min, threshold.max)

        return self.repository.create(sensor_in)

    def list_sensors(
        self, limit: int = 50, offset: int = 0, show_inactive: bool = False
    ) -> list[SensorInfo]:
        """Obtiene y devuelve la lista de sensores paginados"""
        if limit > 50:
            raise LimitExceededError

        return self.repository.list_sensor(limit=limit, offset=offset, show_inactive=show_inactive)

    def get_sensor(self, sensor_id: int | None = None, name: str | None = None) -> SensorInfo:
        """Busca un sensor especifico por ID, nombre o ambos"""
        return ValidateSensorParameters.search_sensor(self.repository, sensor_id, name)

    def update_sensor(
        self,
        sensor_id: int | None,
        name: str | None,
        sensor_in: SensorUpdate,
    ) -> SensorInfo:
        """Reemplaza la informacion completa de un sensor ya existente"""
        sensor = ValidateSensorParameters.search_sensor(self.repository, sensor_id, name)

        if len(sensor_in.name) > 30:
            raise SensorNameTooLongError(sensor_in.name)

        existing_sensor = self.repository.by_name(sensor_in.name)
        if existing_sensor is not None and existing_sensor.id != sensor.id:
            raise SensorNameDuplicateError(sensor_in.name)

        self.validate_sensor_configuration(sensor_in.type, sensor_in.unit)

        threshold = sensor_in.sensor_umbral
        if threshold is None or threshold.min is None or threshold.max is None:
            raise MissingRequiredFieldsError

        self.validate_sensor_threshold(sensor_in.type, sensor_in.unit, threshold.min, threshold.max)

        if (
            sensor_in.name == sensor.name
            and sensor_in.type == sensor.type
            and sensor_in.unit == sensor.unit
            and sensor_in.ubication == sensor.ubication
            and threshold.min == sensor.threshold_min
            and threshold.max == sensor.threshold_max
        ):
            raise NeddedChangesToUpdateSensorError

        return self.repository.update(sensor, sensor_in)

    def deactivate_sensor(self, sensor_id: int | None, name: str | None) -> SensorInfo:
        """Desactiva un sensor (marca inactivo)"""
        sensor = ValidateSensorParameters.search_sensor(self.repository, sensor_id, name)

        if not getattr(sensor, "active", True):
            raise SensorAlreadyInactiveError

        return self.repository.deactivate(sensor)
