import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

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


class SupabaseError(RuntimeError):
    pass


def create_telemetry(payload: schemas.TelemetryCreate) -> dict[str, Any]:
    timestamp = schemas.normalized_timestamp(payload.timestamp)
    row = {
        "device_id": payload.device_id,
        "water_detected": payload.water_detected,
        "measured_distance_cm": payload.measured_distance_cm,
        "water_level_cm": payload.water_level_cm,
        "last_water_level_cm": payload.last_water_level_cm,
        "water_rising": payload.water_rising,
        "system_status": payload.system_status,
        "power_mode": payload.power_mode,
        "timestamp": timestamp.isoformat(),
    }

    telemetry = _request(
        "POST",
        _table("SUPABASE_TELEMETRY_TABLE", "telemetry"),
        body=row,
        prefer="return=representation",
    )[0]

    alert_info = ALERT_STATUSES.get(payload.system_status)
    if alert_info:
        alert_type, message = alert_info
        _request(
            "POST",
            _table("SUPABASE_ALERTS_TABLE", "alerts"),
            body={
                "device_id": payload.device_id,
                "alert_type": alert_type,
                "message": message,
                "water_level_cm": payload.water_level_cm,
                "timestamp": timestamp.isoformat(),
            },
            prefer="return=minimal",
        )

    return telemetry


def get_latest_telemetry() -> dict[str, Any] | None:
    rows = _request(
        "GET",
        _table("SUPABASE_TELEMETRY_TABLE", "telemetry"),
        query={
            "select": "*",
            "order": "timestamp.desc,id.desc",
            "limit": "1",
        },
    )
    return rows[0] if rows else None


def get_telemetry_history(limit: int = 50) -> list[dict[str, Any]]:
    rows = _request(
        "GET",
        _table("SUPABASE_TELEMETRY_TABLE", "telemetry"),
        query={
            "select": "*",
            "order": "timestamp.desc,id.desc",
            "limit": str(max(1, min(limit, 500))),
        },
    )
    return list(reversed(rows))


def get_alerts(limit: int = 50) -> list[dict[str, Any]]:
    return _request(
        "GET",
        _table("SUPABASE_ALERTS_TABLE", "alerts"),
        query={
            "select": "*",
            "order": "timestamp.desc,id.desc",
            "limit": str(max(1, min(limit, 500))),
        },
    )


def health_status() -> dict[str, str]:
    configured = bool(_supabase_url() and _supabase_key())
    return {
        "status": "ok" if configured else "missing_supabase_config",
        "service": "smart-flood-sentinel-backend",
    }


def _request(
    method: str,
    table: str,
    query: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    prefer: str | None = None,
) -> Any:
    url = f"{_supabase_url()}/rest/v1/{table}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    headers = {
        "apikey": _supabase_key(),
        "Authorization": f"Bearer {_supabase_key()}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer

    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else []
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SupabaseError(f"Supabase HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SupabaseError(f"Supabase connection error: {exc.reason}") from exc


def _supabase_url() -> str:
    value = os.getenv("SUPABASE_URL", "").rstrip("/")
    if not value:
        raise SupabaseError("SUPABASE_URL is missing in backend/.env")
    return value


def _supabase_key() -> str:
    value = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
    if not value:
        raise SupabaseError("SUPABASE_SERVICE_ROLE_KEY is missing in backend/.env")
    return value


def _table(env_name: str, default: str) -> str:
    return os.getenv(env_name, default).strip()
