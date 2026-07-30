from datetime import datetime

from sqlalchemy import Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ReadingInfo(Base):
    """Genera el modelo para una lectura, lo que se debe configurar al crear"""

    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(
        ForeignKey("sensors.id", ondelete="cascade"), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(), nullable=False)
    """ Un hash_id es una forma de interpretar lecturas unicas, en la logica de negocios se 
    genera un hash unico para cada lectura, estilo 5d4140... """
    hash_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("sensor_id", "hash_id", name="unique_hash"),
        Index("ix_reading_timestamp", "sensor_id", "timestamp"),
    )
