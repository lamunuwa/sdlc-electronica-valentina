from app.models.sensors import SensorInfo
from app.repositories.sensors import RepositoryProtocol
from app.schemas.sensors import SensorCreate


class SensorDuplicateError(Exception):
    """Excepcion para nombres de sensores duplicados"""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"El sensor con el nombre '{name}' ya existe.")


class SensorService:
    """Clase para el servicio de sensores"""

    def __init__(self, repo: RepositoryProtocol) -> None:
        self.repo = repo

    def create_sensor(self, sensor_in: SensorCreate) -> SensorInfo:
        existing = self.repo.by_name(sensor_in.name)
        if existing:
            raise SensorDuplicateError(sensor_in.name)
        return self.repo.create(sensor_in)
