from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SensorInfo(Base):
    """Clase para la tabla de sensores"""

    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
