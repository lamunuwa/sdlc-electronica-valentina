from app.models.sensors import SensorInfo
from app.repositories.sensors import RepositoryProtocol
from app.schemas.sensors import SensorCreate, SensorUpdate


class SensorDuplicateError(Exception):
    """Excepcion para nombres de sensores duplicados"""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"El sensor con el nombre '{name}' ya existe")


class SensorNotFoundError(Exception):
    """Excepcion para sensores no encontrados"""

    def __init__(self, sensor_id: int) -> None:
        self.sensor_id = sensor_id
        super().__init__(f"El sensor con id '{sensor_id}' no encontrado")


class SensorService:
    """Clase para el servicio de sensores"""

    def __init__(self, repo: RepositoryProtocol) -> None:
        self.repo = repo

    def create_sensors(self, sensor_in: SensorCreate) -> SensorInfo:
        existing = self.repo.by_name(sensor_in.name)
        if existing:
            raise SensorDuplicateError(sensor_in.name)
        return self.repo.create(sensor_in)

    def list_sensors(self) -> list[SensorInfo]:
        return self.repo.list_all()

    def get_sensors(self, sensor_id: int) -> SensorInfo:
        existing = self.repo.by_id(sensor_id)
        if not existing:
            raise SensorNotFoundError(sensor_id)
        return existing

    def update_sensors(self, sensor_id: int, sensor_in: SensorUpdate) -> SensorInfo | None:
        existing = self.repo.by_id(sensor_id)
        if not existing:
            raise SensorNotFoundError(sensor_id)
        if sensor_in.name and sensor_in.name != existing.name:
            duplicate = self.repo.by_name(sensor_in.name)
            if duplicate:
                raise SensorDuplicateError(sensor_in.name)
        return self.repo.update(existing, sensor_in)

    def desactivate_sensors(self, sensor_id: int) -> SensorInfo | None:
        existing = self.repo.by_id(sensor_id)
        if not existing:
            raise SensorNotFoundError(sensor_id)
        return self.repo.desactivate(existing)
