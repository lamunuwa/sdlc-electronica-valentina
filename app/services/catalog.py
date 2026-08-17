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
        """Actualiza la informacion de un sensor. No debe existir ya"""
        sensor = ValidateSensorParameters.search_sensor(self.repository, sensor_id, name)

        update_data = sensor_in.model_dump(exclude_unset=True)
        if not update_data:
            raise NeddedChangesToUpdateSensorError

        was_updated = False

        # Verificamos cambios que no son umbral
        fields = ["name", "type", "unit", "status", "ubication"]
        for field in fields:
            if field in update_data and getattr(sensor, field, None) != update_data[field]:
                was_updated = True
                break

        # Terminamos de verificar con umbrales
        if "sensor_umbral" in update_data and update_data["sensor_umbral"] is not None:
            threshold_data = update_data["sensor_umbral"]

            if "min" in threshold_data and threshold_data["min"] != sensor.threshold_min:
                was_updated = True
            if "max" in threshold_data and threshold_data["max"] != sensor.threshold_max:
                was_updated = True

        if not was_updated:
            raise NeddedChangesToUpdateSensorError

        new_name = sensor_in.name
        if new_name is not None:
            if len(new_name) > 30:
                raise SensorNameTooLongError(new_name)
            existing_sensor = self.repository.by_name(new_name)
            if existing_sensor is not None and existing_sensor.id != sensor.id:
                raise SensorNameDuplicateError(new_name)

        sensor_type = sensor_in.type if sensor_in.type is not None else sensor.type
        sensor_unit = sensor_in.unit if sensor_in.unit is not None else sensor.unit
        self.validate_sensor_configuration(sensor_type, sensor_unit)

        if sensor_in.sensor_umbral is not None:
            threshold = sensor_in.sensor_umbral

            min_val = threshold.min if threshold.min is not None else sensor.threshold_min
            max_val = threshold.max if threshold.max is not None else sensor.threshold_max

            if min_val is None or max_val is None:
                raise MissingRequiredFieldsError

            self.validate_sensor_threshold(sensor_type, sensor_unit, min_val, max_val)

        return self.repository.update(sensor, sensor_in)

    def deactivate_sensor(self, sensor_id: int | None, name: str | None) -> SensorInfo:
        """Desactiva un sensor (marca inactivo)"""
        sensor = ValidateSensorParameters.search_sensor(self.repository, sensor_id, name)

        if not getattr(sensor, "active", True):
            raise SensorAlreadyInactiveError

        return self.repository.deactivate(sensor)
