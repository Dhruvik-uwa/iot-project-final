#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_sleep.h"

#if __has_include("config.h")
#include "config.h"
#else
#include "config.example.h"
#endif

enum SystemStatus {
  SAFE,
  WATER_DETECTED,
  WATER_RISING,
  DRY_RETURNING_TO_SLEEP,
  ERROR_SENSOR_READING
};

struct SensorData {
  bool waterDetected;
  float measuredDistanceCm;
  float waterLevelCm;
  float lastWaterLevelCm;
  bool waterRising;
  SystemStatus status;
};

const unsigned long MONITOR_INTERVAL_MS = 3000;
float lastWaterLevelCm = -1.0;
bool hasBaseline = false;

String statusToString(SystemStatus status) {
  switch (status) {
    case SAFE: return "SAFE";
    case WATER_DETECTED: return "WATER_DETECTED";
    case WATER_RISING: return "WATER_RISING";
    case DRY_RETURNING_TO_SLEEP: return "DRY_RETURNING_TO_SLEEP";
    case ERROR_SENSOR_READING: return "ERROR_SENSOR_READING";
    default: return "ERROR_SENSOR_READING";
  }
}

void beep(int count, int durationMs = 120, int gapMs = 120) {
  for (int i = 0; i < count; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(durationMs);
    digitalWrite(BUZZER_PIN, LOW);
    delay(gapMs);
  }
}

void blinkBothLeds(int count) {
  for (int i = 0; i < count; i++) {
    digitalWrite(GREEN_LED_PIN, HIGH);
    digitalWrite(RED_LED_PIN, HIGH);
    delay(150);
    digitalWrite(GREEN_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, LOW);
    delay(150);
  }
  digitalWrite(GREEN_LED_PIN, HIGH);
}

void blinkRedLed(int count) {
  for (int i = 0; i < count; i++) {
    digitalWrite(RED_LED_PIN, HIGH);
    delay(150);
    digitalWrite(RED_LED_PIN, LOW);
    delay(150);
  }
}

bool readWaterSensor() {
  return digitalRead(WATER_SENSOR_PIN) == HIGH;
}

float measureDistanceCm() {
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH, 30000);
  if (duration == 0) {
    return -1.0;
  }

  return duration * 0.0343 / 2.0;
}

float calculateWaterLevel(float measuredDistanceCm) {
  float level = INSTALL_HEIGHT_CM - measuredDistanceCm;
  return level < 0 ? 0 : level;
}

String buildTelemetryPayload(const SensorData &data) {
  String payload = "{";
  payload += "\"device_id\":\"" DEVICE_ID "\",";
  payload += "\"water_detected\":" + String(data.waterDetected ? "true" : "false") + ",";
  payload += "\"measured_distance_cm\":" + String(data.measuredDistanceCm, 2) + ",";
  payload += "\"water_level_cm\":" + String(data.waterLevelCm, 2) + ",";
  payload += "\"last_water_level_cm\":" + String(data.lastWaterLevelCm, 2) + ",";
  payload += "\"water_rising\":" + String(data.waterRising ? "true" : "false") + ",";
  payload += "\"system_status\":\"" + statusToString(data.status) + "\",";
  payload += "\"power_mode\":\"" POWER_MODE_LABEL "\",";
  payload += "\"timestamp\":\"\"";
  payload += "}";
  return payload;
}

void sendToCloudPlatform(const String &payload) {
  Serial.println("[cloud placeholder] " + payload);
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");

  unsigned long startedAt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startedAt < 10000) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi connected: " + WiFi.localIP().toString());
  } else {
    Serial.println("Wi-Fi unavailable, telemetry will only be printed.");
  }
}

void sendTelemetryToBackend(const SensorData &data) {
  String payload = buildTelemetryPayload(data);
  Serial.println("[telemetry] " + payload);
  sendToCloudPlatform(payload);

  connectWiFi();
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  HTTPClient http;
  http.begin(BACKEND_URL);
  http.addHeader("Content-Type", "application/json");
  int responseCode = http.POST(payload);
  Serial.println("Backend response: " + String(responseCode));
  http.end();
}

void enterDeepSleep() {
  Serial.println("Entering deep sleep.");
  digitalWrite(RED_LED_PIN, LOW);

  if (DEMO_GREEN_LED_DURING_SLEEP) {
    digitalWrite(GREEN_LED_PIN, HIGH);
  } else {
    digitalWrite(GREEN_LED_PIN, LOW);
  }

  esp_sleep_enable_ext0_wakeup((gpio_num_t)WATER_SENSOR_PIN, 1);
  delay(250);
  esp_deep_sleep_start();
}

void handleDryState() {
  SensorData data = {
    false,
    0.0,
    0.0,
    hasBaseline ? lastWaterLevelCm : 0.0,
    false,
    DRY_RETURNING_TO_SLEEP
  };
  sendTelemetryToBackend(data);
  enterDeepSleep();
}

void monitorWater() {
  Serial.println("Monitoring water every 3 seconds.");

  while (true) {
    bool waterDetected = readWaterSensor();
    if (!waterDetected) {
      handleDryState();
    }

    float distanceCm = measureDistanceCm();
    if (distanceCm < 0) {
      SensorData errorData = {
        true,
        -1.0,
        0.0,
        hasBaseline ? lastWaterLevelCm : 0.0,
        false,
        ERROR_SENSOR_READING
      };
      digitalWrite(RED_LED_PIN, HIGH);
      sendTelemetryToBackend(errorData);
      delay(MONITOR_INTERVAL_MS);
      continue;
    }

    float currentLevel = calculateWaterLevel(distanceCm);
    bool waterRising = false;
    SystemStatus status = WATER_DETECTED;

    if (!hasBaseline) {
      Serial.println("First water detection.");
      lastWaterLevelCm = currentLevel;
      hasBaseline = true;
      digitalWrite(RED_LED_PIN, HIGH);
      beep(2);
      blinkBothLeds(2);
    } else if (currentLevel - lastWaterLevelCm > 0) {
      Serial.println("Water level rising.");
      waterRising = true;
      status = WATER_RISING;
      digitalWrite(RED_LED_PIN, HIGH);
      beep(3);
      blinkRedLed(3);
    } else {
      Serial.println("Water level same or falling.");
      digitalWrite(RED_LED_PIN, HIGH);
      lastWaterLevelCm = currentLevel;
    }

    SensorData data = {
      true,
      distanceCm,
      currentLevel,
      lastWaterLevelCm,
      waterRising,
      status
    };
    sendTelemetryToBackend(data);

    if (waterRising) {
      lastWaterLevelCm = currentLevel;
    }

    delay(MONITOR_INTERVAL_MS);
  }
}

void setupPins() {
  pinMode(WATER_SENSOR_PIN, INPUT);
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);

  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, HIGH);
}

void setup() {
  Serial.begin(115200);
  delay(200);
  setupPins();
  beep(1);

  esp_sleep_wakeup_cause_t wakeupReason = esp_sleep_get_wakeup_cause();
  Serial.println("Wakeup reason: " + String((int)wakeupReason));

  bool wokeFromWaterSensor = wakeupReason == ESP_SLEEP_WAKEUP_EXT0;
  bool waterDetected = wokeFromWaterSensor || readWaterSensor();

  if (waterDetected) {
    monitorWater();
  } else {
    SensorData safeData = { false, 0.0, 0.0, 0.0, false, SAFE };
    sendTelemetryToBackend(safeData);
    enterDeepSleep();
  }
}

void loop() {
}

