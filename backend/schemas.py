from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class TelemetryCreate(BaseModel):
    device_id: str = "esp32-flood-001"
    water_detected: bool = False
    measured_distance_cm: float = 0.0
    water_level_cm: float = 0.0
    last_water_level_cm: float = 0.0
    water_rising: bool = False
    system_status: str = "SAFE"
    power_mode: str = "USB_OR_BATTERY"
    timestamp: Optional[datetime | str] = None

    @field_validator("timestamp")
    @classmethod
    def parse_empty_timestamp(cls, value):
        if value in (None, ""):
            return None
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class TelemetryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    water_detected: bool
    measured_distance_cm: float
    water_level_cm: float
    last_water_level_cm: float
    water_rising: bool
    system_status: str
    power_mode: str
    timestamp: datetime


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    alert_type: str
    message: str
    water_level_cm: float
    timestamp: datetime


class HealthRead(BaseModel):
    status: str
    service: str


def normalized_timestamp(value):
    return value or datetime.now(timezone.utc)

