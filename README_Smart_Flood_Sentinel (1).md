# Smart Flood Sentinel for Residential Security

## 1. Project Overview

**Smart Flood Sentinel for Residential Security** is an IoT-based residential flood and water-leak early-warning system using an ESP32 / FireBeetle ESP32 board. The system is designed to monitor vulnerable household locations such as laundries, bathrooms, kitchens, drainage corners, or other low-visibility areas where leaks and localised flooding may begin unnoticed.

The project combines a **water leak sensor** and an **ultrasonic sensor** to detect both direct surface water and rising water level. When water is detected, the ESP32 wakes from deep sleep, measures the water level, triggers local LED and buzzer alerts, and prepares telemetry data for a backend, frontend dashboard, and later IoT cloud platform integration.

This README includes the full hardware behaviour, firmware logic, backend API, frontend dashboard, database structure, cloud-ready design, and expected demo flow.

---

## 2. Important Scope Rule

Only the hardware listed in this README should be used.

Do **not** add extra hardware, extra sensors, relay modules, ESP32-CAM, water flow sensor, pumps, motors, or other components.

This project must stay focused on the current MVP hardware and software requirements.

---

## 3. Hardware to Use Only

The project uses only the following hardware:

| Component | Quantity / Notes |
|---|---:|
| ESP32 / FireBeetle ESP32 board | 1 |
| Water leak sensor | 1 |
| Ultrasonic sensor | 1 |
| Piezo buzzer | 1 |
| LEDs | 15 available, but only simple status LEDs are required |
| Resistors pack | 1 |
| Power supplies | 2 |
| USB power | Primary power source |
| 3.7V lithium battery | Backup power through FireBeetle onboard JST port |

### Hardware Restriction

Do not include:

- Relay module
- ESP32-CAM
- Water flow sensor
- Pump
- Motor
- Extra sensors
- Any hardware not listed above

---

## 4. Project Purpose

The system should:

1. Stay in low-power deep sleep when no water is detected.
2. Wake up when the water leak sensor detects water.
3. Use the ultrasonic sensor only after water is detected.
4. Calculate water level using ultrasonic distance.
5. Alarm immediately on first water detection.
6. Alarm again only when the water level is rising.
7. Stay silent when the water level is the same or falling.
8. Return to deep sleep when the water sensor becomes dry.
9. Send or prepare sensor readings for backend and frontend display.
10. Keep the software structure ready for future IoT cloud platform integration.

---

## 5. Full System Architecture

The complete MVP should include four main parts:

```text
Water Leak Sensor + Ultrasonic Sensor
              |
              v
      ESP32 / FireBeetle
              |
              | Local alert
              v
       LEDs + Piezo Buzzer
              |
              | Telemetry payload
              v
          Backend API
              |
              v
      Frontend Dashboard
              |
              v
 Future IoT Cloud Platform Integration
```

### System Modules

1. **Sensing module**
   - Water leak sensor detects direct surface water.
   - Ultrasonic sensor measures distance and supports water-level calculation.

2. **Edge processing module**
   - ESP32 reads sensors, handles wakeup logic, calculates water level, and decides whether to alarm.

3. **Local alert module**
   - LEDs show simple system status.
   - Piezo buzzer provides audible warnings.

4. **Backend module**
   - Receives telemetry from ESP32.
   - Stores readings and alert events.
   - Provides data to the frontend dashboard.

5. **Frontend dashboard module**
   - Displays latest sensor status, water level, alert history, and charts.

6. **Future IoT cloud module**
   - Code should be structured so a cloud platform can be added later.

---

## 6. Firmware Behaviour

The ESP32 firmware is responsible for:

- Pin setup
- Sensor reading
- Wakeup reason checking
- Deep sleep control
- Ultrasonic distance measurement
- Water-level calculation
- LED control
- Buzzer control
- Alarm logic
- Backend telemetry sending
- Future cloud payload preparation

---

## 7. Startup Behaviour

When the ESP32 powers on:

1. Initialize all pins.
2. Turn the green LED on.
3. Make the buzzer beep once as a startup self-test.
4. Check the ESP32 wakeup reason.

### If ESP32 woke up because of the water sensor

- Immediately flag water as detected.
- Activate/read the ultrasonic sensor.
- Start the water monitoring loop.

### If it is a normal boot

- Check the water sensor once.
- If water is detected, start monitoring.
- If no water is detected, enter deep sleep immediately.

---

## 8. Sleep State

When no water is detected:

- ESP32 enters deep sleep.
- The water sensor TTL pin acts as the wakeup interrupt.
- When the water sensor TTL pin goes HIGH, the ESP32 wakes up.
- Green LED may remain on during demo mode.
- For real battery-saving mode, the green LED should turn off before deep sleep.

### Note on Green LED and Deep Sleep

Keeping an LED on during deep sleep consumes power. For classroom/demo visibility, the green LED may stay on. For better battery life, the firmware should allow the green LED to turn off before deep sleep.

---

## 9. Wakeup Monitoring Loop

After the ESP32 wakes because water is detected, it should run the monitoring loop every **3 seconds**.

Each cycle should:

1. Read the water sensor TTL pin.
2. If water is detected, activate/read the ultrasonic sensor.
3. Measure distance using the ultrasonic sensor.
4. Calculate water level.
5. Decide whether to sound an alarm.
6. Send telemetry to backend.
7. Prepare data for future IoT cloud upload.
8. Return to deep sleep when the sensor becomes dry.

---

## 10. Water Level Calculation

The ultrasonic sensor measures distance from the installed sensor position to the water surface.

Use this formula:

```cpp
water_level_cm = install_height_cm - measured_distance_cm;
```

Where:

- `install_height_cm` is the fixed height of the ultrasonic sensor above the base/floor.
- `measured_distance_cm` is the distance measured by the ultrasonic sensor.
- `water_level_cm` is the calculated water level.

Example:

```text
install_height_cm = 20 cm
measured_distance_cm = 12 cm
water_level_cm = 20 - 12 = 8 cm
```

---

## 11. First Water Detection Logic

If this is the first valid water-level reading after wakeup:

- Trigger an immediate alarm.
- Buzzer beeps 2 times.
- Red and green LEDs both blink.
- Save the first water-level value as the baseline.

This ensures the user is alerted as soon as water is detected.

---

## 12. Rising Water Alarm Logic

For every later reading, compare the current water level with the previous water level.

Use this exact core logic:

```cpp
if (current_level - last_level > 0) {
    // Water is rising
    alarm();
} else {
    // Water is same or falling
    no_alarm();
    update_baseline();
}
```

### Behaviour

| Condition | Action |
|---|---|
| Current level is higher than last level | Alarm, buzzer 3 beeps |
| Current level is same as last level | No alarm, update baseline |
| Current level is lower than last level | No alarm, update baseline |
| Water sensor becomes dry | Turn red LED off and return to deep sleep |

---

## 13. LED Logic

Keep LED behaviour simple and reliable.

### Green LED

- ON during safe/startup/demo standby mode.
- Can blink during first water detection alarm.
- Can turn off before deep sleep for better battery saving.

### Red LED

- ON or blinking when water is detected.
- Blinks when water level is rising.
- OFF when the water sensor becomes dry.

### Available LEDs

Although 15 LEDs are available, the MVP should not overcomplicate LED logic. Simple status indication is enough.

Recommended basic setup:

| LED | Purpose |
|---|---|
| Green LED | Safe/standby/demo mode |
| Red LED | Water detected/rising alert |

Optional later use:

- Additional LEDs can be used as a simple water-level bar indicator if required, but this is not necessary for the MVP.

---

## 14. Buzzer Logic

Use these buzzer patterns:

| Event | Buzzer Pattern |
|---|---|
| Startup self-test | 1 beep |
| First water detection | 2 beeps |
| Water level rising | 3 beeps |
| Water level same or falling | No beep |
| Dry state | No beep, return to sleep |

---

## 15. Power Logic

The system should support:

1. Primary power through USB.
2. Backup power using a 3.7V lithium battery connected to the FireBeetle onboard JST port.
3. Automatic switch to battery when USB is disconnected.
4. Battery recharge when USB is reconnected.
5. Deep sleep to reduce battery consumption.

The FireBeetle onboard charging circuit is assumed to handle USB/battery switching and charging.

---

## 16. System Status Values

Use these firmware/backend/frontend status values:

```text
SAFE
WATER_DETECTED
WATER_RISING
DRY_RETURNING_TO_SLEEP
ERROR_SENSOR_READING
```

### Status Meaning

| Status | Meaning |
|---|---|
| `SAFE` | No water detected |
| `WATER_DETECTED` | Water sensor detected water |
| `WATER_RISING` | Water level is increasing |
| `DRY_RETURNING_TO_SLEEP` | Sensor became dry and ESP32 is returning to sleep |
| `ERROR_SENSOR_READING` | Invalid or failed sensor reading |

---

## 17. IoT Cloud Platform Plan

Later, this project will use an IoT cloud platform.

The current system should not be locked to one specific platform yet.

Possible future platforms:

- Arduino IoT Cloud
- Blynk
- ThingsBoard
- AWS IoT
- Firebase
- Azure IoT

For now, the firmware should include a modular placeholder function:

```cpp
sendToCloudPlatform(sensorData);
```

At this stage, the function can:

- Print payload data to the Serial Monitor, or
- Contain placeholder code, or
- Forward data to backend first.

The backend should also include a placeholder cloud-forwarding module so cloud integration can be added later without restructuring the whole project.

---

## 18. Cloud-Ready Telemetry Payload

The ESP32 should prepare a JSON-style payload like this:

```json
{
  "device_id": "esp32-flood-001",
  "water_detected": true,
  "measured_distance_cm": 12.5,
  "water_level_cm": 7.5,
  "last_water_level_cm": 6.8,
  "water_rising": true,
  "system_status": "WATER_RISING",
  "power_mode": "USB_OR_BATTERY",
  "timestamp": "placeholder-or-generated"
}
```

### Payload Fields

| Field | Description |
|---|---|
| `device_id` | Unique ESP32/device name |
| `water_detected` | Boolean water sensor state |
| `measured_distance_cm` | Ultrasonic distance reading |
| `water_level_cm` | Calculated water level |
| `last_water_level_cm` | Previous water level baseline |
| `water_rising` | Boolean rising-water state |
| `system_status` | Current system status |
| `power_mode` | USB/battery placeholder |
| `timestamp` | Timestamp placeholder or backend-generated time |

---

## 19. Backend Requirements

The backend should receive, store, and provide sensor data to the frontend dashboard.

### Recommended Backend Stack

- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- CORS support for frontend access

### Backend Responsibilities

The backend should:

1. Receive telemetry data from the ESP32.
2. Store sensor readings in a SQLite database.
3. Store alert events when water is detected or rising.
4. Provide the latest status to the frontend.
5. Provide historical readings for charts.
6. Provide alert history for dashboard display.
7. Include a placeholder to forward data to an IoT cloud platform later.

---

## 20. Backend API Endpoints

### `POST /api/telemetry`

Receives telemetry data from the ESP32.

Example request body:

```json
{
  "device_id": "esp32-flood-001",
  "water_detected": true,
  "measured_distance_cm": 12.5,
  "water_level_cm": 7.5,
  "last_water_level_cm": 6.8,
  "water_rising": true,
  "system_status": "WATER_RISING",
  "power_mode": "USB_OR_BATTERY",
  "timestamp": "auto-generated if missing"
}
```

Expected behaviour:

- Save telemetry to database.
- Automatically create alert records if status is abnormal.
- Return saved telemetry response.

---

### `GET /api/telemetry/latest`

Returns the latest sensor reading.

---

### `GET /api/telemetry/history`

Returns recent telemetry records for dashboard charts.

Optional query parameter:

```text
limit=50
```

---

### `GET /api/alerts`

Returns alert history.

---

### `GET /api/health`

Returns backend health status.

Example response:

```json
{
  "status": "ok",
  "service": "smart-flood-sentinel-backend"
}
```

---

## 21. Database Models

The backend should use two main database tables.

### Telemetry Table

Fields:

| Field | Type / Meaning |
|---|---|
| `id` | Primary key |
| `device_id` | ESP32 device ID |
| `water_detected` | Boolean |
| `measured_distance_cm` | Float |
| `water_level_cm` | Float |
| `last_water_level_cm` | Float |
| `water_rising` | Boolean |
| `system_status` | String |
| `power_mode` | String |
| `timestamp` | Date/time |

### Alerts Table

Fields:

| Field | Type / Meaning |
|---|---|
| `id` | Primary key |
| `device_id` | ESP32 device ID |
| `alert_type` | Alert category |
| `message` | Human-readable alert message |
| `water_level_cm` | Water level at alert time |
| `timestamp` | Date/time |

### Alert Types

```text
FIRST_WATER_DETECTION
WATER_RISING
DRY_RETURNING_TO_SLEEP
ERROR_SENSOR_READING
```

---

## 22. Frontend Dashboard Requirements

The frontend dashboard should display the current system condition and historical readings clearly during a demo.

### Recommended Frontend Stack

- React
- Vite
- JavaScript or TypeScript
- Recharts or another simple chart library
- CSS/Tailwind/simple styling

---

## 23. Dashboard Sections

### 1. Status Overview

Display summary cards for:

- System Status
- Water Sensor
- Water Level
- Ultrasonic Distance
- Water Rising
- Power Mode

Recommended colours:

| Status | Colour |
|---|---|
| Safe | Green |
| Water detected | Yellow/Orange |
| Water rising / critical alert | Red |
| No recent data | Grey |

---

### 2. Live Sensor Display

Show latest values:

- Water detected: Yes/No
- Measured distance in cm
- Water level in cm
- Last water level in cm
- Water rising: Yes/No
- Device ID
- Timestamp

The dashboard should auto-refresh every **3 seconds**.

---

### 3. Alert History

Show a table with:

- Time
- Device ID
- Alert Type
- Message
- Water Level

---

### 4. Charts

Show simple charts for:

- Water level over time
- Ultrasonic distance over time

The charts should help show whether water is rising, stable, or falling.

---

## 24. Frontend UI Style

The dashboard should be:

- Clean
- Modern
- Simple
- Responsive
- Easy to understand during a university demo
- Not overcomplicated

Use:

- Clear cards
- Simple spacing
- Status colours
- Readable labels
- A minimal chart layout
- Alert table with clear timestamps

Do not add:

- Login system
- Payment features
- User management
- Complex admin settings
- Overcomplicated UI

---

## 25. Expected Project Structure

Create this structure:

```text
smart-flood-sentinel/
│
├── firmware/
│   └── smart_flood_sentinel/
│       ├── smart_flood_sentinel.ino
│       ├── config.example.h
│       └── README.md
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── cloud_forwarder.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       ├── components/
│       │   ├── StatusCard.jsx
│       │   ├── SensorOverview.jsx
│       │   ├── AlertHistory.jsx
│       │   └── SensorCharts.jsx
│       └── styles.css
│
└── README.md
```

---

## 26. Firmware File Requirements

The firmware should include:

- Clear pin definitions
- Wi-Fi/backend configuration placeholder
- Wakeup reason check
- Deep sleep setup
- Water sensor reading function
- Ultrasonic distance measurement function
- Water level calculation function
- First detection alarm logic
- Rising water alarm logic
- LED control functions
- Buzzer helper function
- JSON payload preparation
- Send telemetry to backend API
- Placeholder cloud sending function
- Serial Monitor debugging

---

## 27. Backend File Requirements

The backend should include:

- FastAPI app
- SQLite database setup
- SQLAlchemy models
- Pydantic schemas
- CRUD helpers
- API routes
- CORS configuration
- Automatic timestamp creation
- Alert creation based on received system status
- Cloud forwarder placeholder

---

## 28. Frontend File Requirements

The frontend should include:

- React + Vite setup
- API helper file
- Auto-refresh for latest telemetry every 3 seconds
- Fetch telemetry history
- Fetch alert history
- Status cards
- Sensor overview panel
- Alert table
- Charts
- Responsive styling

---

## 29. How to Run the Backend

From the backend folder:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend should run at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

---

## 30. How to Run the Frontend

From the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

Frontend should run at a Vite local development URL such as:

```text
http://localhost:5173
```

---

## 31. How to Upload Firmware

Using Arduino IDE:

1. Open `firmware/smart_flood_sentinel/smart_flood_sentinel.ino`.
2. Select the correct ESP32 board.
3. Select the correct COM port.
4. Update Wi-Fi/backend placeholders in `config.example.h` or copied `config.h`.
5. Upload the firmware.
6. Open Serial Monitor.
7. Set baud rate to `115200`.
8. Observe startup, sleep, wakeup, and sensor logs.

---

## 32. Testing Plan

### Hardware Tests

1. Power on ESP32.
2. Confirm green LED turns on.
3. Confirm buzzer beeps once.
4. Confirm no-water state enters deep sleep.
5. Add water to leak sensor.
6. Confirm ESP32 wakes.
7. Confirm ultrasonic sensor reads distance.
8. Confirm first water detection causes 2 buzzer beeps.
9. Increase water level.
10. Confirm rising water causes 3 buzzer beeps.
11. Keep water same/falling.
12. Confirm no buzzer alarm.
13. Dry the water sensor.
14. Confirm red LED turns off and ESP32 returns to deep sleep.

### Backend Tests

1. Start FastAPI backend.
2. Send test telemetry using Swagger UI or curl.
3. Confirm telemetry is saved.
4. Confirm alert records are created for abnormal states.
5. Confirm latest endpoint returns newest reading.
6. Confirm history endpoint returns multiple records.
7. Confirm alerts endpoint returns alert history.

### Frontend Tests

1. Start frontend dashboard.
2. Confirm latest status cards load.
3. Confirm alert history table loads.
4. Confirm charts display telemetry history.
5. Confirm auto-refresh updates every 3 seconds.
6. Confirm status colours match system status.

---

## 33. Expected Demo Flow

1. Start backend.
2. Start frontend dashboard.
3. Power on ESP32.
4. Green LED turns on.
5. Buzzer beeps once.
6. ESP32 checks the water sensor.
7. If no water is detected, ESP32 enters deep sleep.
8. Water leak sensor detects water.
9. ESP32 wakes up.
10. Ultrasonic sensor measures distance.
11. Water level is calculated.
12. First detection triggers 2 buzzer beeps and LED blinking.
13. ESP32 sends telemetry to backend.
14. Frontend dashboard updates current status.
15. If water level rises, buzzer beeps 3 times.
16. Backend records a water-rising alert.
17. Dashboard shows alert history and chart updates.
18. If the sensor becomes dry, red LED turns off.
19. ESP32 sends dry/safe status.
20. ESP32 returns to deep sleep.

---

## 34. What Codex Should Generate

Codex should generate clean, working, well-commented code for:

1. ESP32 firmware
2. FastAPI backend
3. SQLite database models
4. Backend API routes
5. Cloud forwarder placeholder
6. React frontend dashboard
7. Sensor status cards
8. Alert history table
9. Sensor charts
10. README files

---

## 35. Do Not Include

Do not include:

- Extra hardware
- Relay module
- ESP32-CAM
- Water flow sensor
- Pumps
- Motors
- Extra sensors
- Complex authentication
- Login/signup system
- Payment features
- Admin dashboard
- Production cloud deployment unless only as placeholder
- Overcomplicated UI

---

## 36. Final MVP Summary

The final MVP should demonstrate a complete IoT pipeline:

```text
Water detected → ESP32 wakes → Ultrasonic measures level → Alarm logic runs → LED/buzzer alert → Telemetry sent to backend → Dashboard updates → Cloud-ready payload prepared
```

The core value of the project is that it combines:

- Direct water detection
- Rising water-level monitoring
- Local alarm response
- Low-power deep sleep
- Backend telemetry storage
- Frontend dashboard visualisation
- Future IoT cloud platform readiness
