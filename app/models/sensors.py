from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SensorInfo(Base):
    """Genera el modelo para un sensor, lo que se debe configurar al crear"""

    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold_min: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_max: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)

    @property
    def sensor_umbral(self) -> dict[str, float]:
        return {"min": self.threshold_min, "max": self.threshold_max}
