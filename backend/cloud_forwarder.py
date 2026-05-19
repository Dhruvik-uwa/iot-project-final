import json
import os
import urllib.error
import urllib.request

from models import Alert, Telemetry


def forward_to_cloud_platform(telemetry: Telemetry) -> None:
    """Forward telemetry to Supabase REST when cloud credentials are configured."""
    payload = {
        "device_id": telemetry.device_id,
        "water_detected": telemetry.water_detected,
        "measured_distance_cm": telemetry.measured_distance_cm,
        "water_level_cm": telemetry.water_level_cm,
        "last_water_level_cm": telemetry.last_water_level_cm,
        "water_rising": telemetry.water_rising,
        "system_status": telemetry.system_status,
        "power_mode": telemetry.power_mode,
        "timestamp": telemetry.timestamp.isoformat(),
    }
    _insert_supabase_row(_table_name("SUPABASE_TELEMETRY_TABLE", "telemetry"), payload)


def forward_alert_to_cloud_platform(alert: Alert) -> None:
    payload = {
        "device_id": alert.device_id,
        "alert_type": alert.alert_type,
        "message": alert.message,
        "water_level_cm": alert.water_level_cm,
        "timestamp": alert.timestamp.isoformat(),
    }
    _insert_supabase_row(_table_name("SUPABASE_ALERTS_TABLE", "alerts"), payload)


def _table_name(env_name: str, default: str) -> str:
    return os.getenv(env_name, default).strip()


def _insert_supabase_row(table: str, payload: dict) -> None:
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

    if not supabase_url or not supabase_key:
        print("[supabase skipped] Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to enable cloud upload.")
        return

    request = urllib.request.Request(
        f"{supabase_url}/rest/v1/{table}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            print(f"[supabase uploaded] {table}: HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"[supabase error] {table}: HTTP {exc.code} {detail}")
    except urllib.error.URLError as exc:
        print(f"[supabase error] {table}: {exc.reason}")
