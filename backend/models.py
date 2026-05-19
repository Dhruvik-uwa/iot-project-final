from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(80), index=True)
    water_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    measured_distance_cm: Mapped[float] = mapped_column(Float, default=0.0)
    water_level_cm: Mapped[float] = mapped_column(Float, default=0.0)
    last_water_level_cm: Mapped[float] = mapped_column(Float, default=0.0)
    water_rising: Mapped[bool] = mapped_column(Boolean, default=False)
    system_status: Mapped[str] = mapped_column(String(60), index=True)
    power_mode: Mapped[str] = mapped_column(String(60), default="USB_OR_BATTERY")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(80), index=True)
    alert_type: Mapped[str] = mapped_column(String(80), index=True)
    message: Mapped[str] = mapped_column(String(255))
    water_level_cm: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

