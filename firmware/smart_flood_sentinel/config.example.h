#pragma once

// Copy this file to config.h and update values for your wiring/network.

#define WIFI_SSID "YOUR_WIFI_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define BACKEND_URL "http://127.0.0.1:8000/api/telemetry"

#define DEVICE_ID "esp32-flood-001"
#define POWER_MODE_LABEL "USB_OR_BATTERY"

// Pin placeholders. Update to match your ESP32 / FireBeetle wiring.
#define WATER_SENSOR_PIN 33
#define ULTRASONIC_TRIG_PIN 25
#define ULTRASONIC_ECHO_PIN 26
#define BUZZER_PIN 27
#define GREEN_LED_PIN 14
#define RED_LED_PIN 12

// Fixed ultrasonic installation height above the floor/base.
#define INSTALL_HEIGHT_CM 20.0

// Keep green LED on during deep sleep for classroom demo visibility.
// Set to 0 for better battery saving.
#define DEMO_GREEN_LED_DURING_SLEEP 1

