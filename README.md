# Smart Flood Sentinel for Residential Security

Smart Flood Sentinel is an IoT flood and leak early-warning MVP for residential spaces. It uses an ESP32 / FireBeetle ESP32, a water leak sensor, an ultrasonic sensor, simple LEDs, and a piezo buzzer. The ESP32 detects water, measures level changes, alerts locally, sends telemetry to a FastAPI backend, stores live data in Supabase, and feeds a React dashboard.

## Project Structure

```text
firmware/
  smart_flood_sentinel/
backend/
frontend/
README_Smart_Flood_Sentinel (1).md
```

## Hardware Scope

Use only:

- ESP32 / FireBeetle ESP32 board
- Water leak sensor
- Ultrasonic sensor
- Piezo buzzer
- Simple status LEDs
- Resistors
- USB power
- 3.7V lithium battery through the FireBeetle JST port

Do not add relay modules, pumps, motors, cameras, flow sensors, or extra sensors.

## Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend URL: `http://127.0.0.1:8000`

Health check: `http://127.0.0.1:8000/api/health`

### Supabase IoT Platform

The backend uses Supabase as the live database. Run `backend/supabase_schema.sql` in the Supabase SQL Editor, then put these values in `backend/.env`:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_TELEMETRY_TABLE=telemetry
SUPABASE_ALERTS_TABLE=alerts
```

Keep the service role key on the backend only, never in the ESP32 firmware.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

For Vercel, deploy the `frontend` folder and set:

```env
VITE_API_BASE_URL=https://your-live-backend-url.example.com
```

The Vercel dashboard cannot call a backend running on your laptop at `127.0.0.1`; the backend also needs a public URL.

## Firmware

1. Open `firmware/smart_flood_sentinel/smart_flood_sentinel.ino` in Arduino IDE.
2. Copy `config.example.h` to `config.h`.
3. Update Wi-Fi credentials, backend URL, pins, and install height.
4. Select the ESP32 board and COM port.
5. Upload and open Serial Monitor at `115200`.

## Demo Flow

1. Start backend.
2. Start frontend.
3. Power ESP32.
4. Startup beep confirms boot.
5. Dry sensor enters deep sleep.
6. Water sensor wakes ESP32.
7. Ultrasonic sensor calculates water level.
8. First detection triggers two beeps.
9. Rising water triggers three beeps.
10. Telemetry appears in backend and dashboard.
11. Dry sensor sends dry status and returns to sleep.

## API Summary

- `GET /api/health`
- `POST /api/telemetry`
- `GET /api/telemetry/latest`
- `GET /api/telemetry/history?limit=50`
- `GET /api/alerts`
