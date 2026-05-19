# Smart Flood Sentinel Backend

FastAPI backend for receiving ESP32 telemetry, storing Supabase history, creating alert records, and serving dashboard data.

## Run

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

- `GET /api/health`
- `POST /api/telemetry`
- `GET /api/telemetry/latest`
- `GET /api/telemetry/history?limit=50`
- `GET /api/alerts?limit=50`

## Supabase Database

The backend uses Supabase as the live database. It does not use local SQLite for API data.

1. Open Supabase SQL Editor.
2. Run `backend/supabase_schema.sql`.
3. Put your credentials in `backend/.env`.

`backend/.env` should contain:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_TELEMETRY_TABLE=telemetry
SUPABASE_ALERTS_TABLE=alerts
```

Keep the service role key on the backend only. Do not put it in ESP32 firmware or frontend code.

## Example Telemetry

```json
{
  "device_id": "esp32-flood-001",
  "water_detected": true,
  "measured_distance_cm": 12.5,
  "water_level_cm": 7.5,
  "last_water_level_cm": 6.8,
  "water_rising": true,
  "system_status": "WATER_RISING",
  "power_mode": "USB_OR_BATTERY"
}
```
