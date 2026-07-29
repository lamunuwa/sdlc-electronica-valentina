from datetime import datetime

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ReadingInfo(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(
        ForeignKey("sensors.id", ondelete="cascade"), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(), nullable=False)
    # hash_id es una forma de identificacion unica, revisa cada lectura y genera un codigo
    # inmutable estilo "a7b8c9d...", ayuda a identificar duplicados
    hash_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("sensor_id", "hash_id", name="unique_hash"),)
