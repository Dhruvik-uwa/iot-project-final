from sqlalchemy import desc
from sqlalchemy.orm import Session

import models
import schemas

ALERT_STATUSES = {
    "WATER_DETECTED": (
        "FIRST_WATER_DETECTION",
        "Water has been detected by the leak sensor.",
    ),
    "WATER_RISING": (
        "WATER_RISING",
        "Water level is rising.",
    ),
    "DRY_RETURNING_TO_SLEEP": (
        "DRY_RETURNING_TO_SLEEP",
        "Water sensor is dry. Device is returning to sleep.",
    ),
    "ERROR_SENSOR_READING": (
        "ERROR_SENSOR_READING",
        "A sensor reading failed or was invalid.",
    ),
}


def create_telemetry(db: Session, payload: schemas.TelemetryCreate) -> models.Telemetry:
    telemetry = models.Telemetry(
        device_id=payload.device_id,
        water_detected=payload.water_detected,
        measured_distance_cm=payload.measured_distance_cm,
        water_level_cm=payload.water_level_cm,
        last_water_level_cm=payload.last_water_level_cm,
        water_rising=payload.water_rising,
        system_status=payload.system_status,
        power_mode=payload.power_mode,
        timestamp=schemas.normalized_timestamp(payload.timestamp),
    )
    db.add(telemetry)
    db.flush()

    alert_info = ALERT_STATUSES.get(payload.system_status)
    if alert_info:
        alert_type, message = alert_info
        db.add(
            models.Alert(
                device_id=payload.device_id,
                alert_type=alert_type,
                message=message,
                water_level_cm=payload.water_level_cm,
                timestamp=telemetry.timestamp,
            )
        )

    db.commit()
    db.refresh(telemetry)
    return telemetry


def get_latest_telemetry(db: Session) -> models.Telemetry | None:
    return db.query(models.Telemetry).order_by(desc(models.Telemetry.timestamp), desc(models.Telemetry.id)).first()


def get_telemetry_history(db: Session, limit: int = 50) -> list[models.Telemetry]:
    limit = max(1, min(limit, 500))
    rows = (
        db.query(models.Telemetry)
        .order_by(desc(models.Telemetry.timestamp), desc(models.Telemetry.id))
        .limit(limit)
        .all()
    )
    return list(reversed(rows))


def get_alerts(db: Session, limit: int = 50) -> list[models.Alert]:
    limit = max(1, min(limit, 500))
    return (
        db.query(models.Alert)
        .order_by(desc(models.Alert.timestamp), desc(models.Alert.id))
        .limit(limit)
        .all()
    )

