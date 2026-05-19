# ESP32 Firmware

This sketch implements the Smart Flood Sentinel edge behaviour:

- Startup self-test beep
- Water sensor wakeup logic
- Deep sleep when dry
- Ultrasonic distance measurement after water detection
- Water-level calculation
- First-water and rising-water buzzer/LED alarms
- Backend telemetry POST
- Cloud-platform placeholder

## Setup

1. Copy `config.example.h` to `config.h`.
2. Update Wi-Fi, backend URL, pins, and `INSTALL_HEIGHT_CM`.
3. Open `smart_flood_sentinel.ino` in Arduino IDE.
4. Install/select the ESP32 board package.
5. Upload and open Serial Monitor at `115200`.

## Arduino Libraries

The sketch uses ESP32 core libraries:

- `WiFi.h`
- `HTTPClient.h`
- `esp_sleep.h`

No additional hardware is required beyond the project README scope.

