import { useEffect, useMemo, useState } from "react";
import { Activity, BatteryCharging, Droplets, Gauge, Power, Ruler } from "lucide-react";
import AlertHistory from "./components/AlertHistory.jsx";
import SensorCharts from "./components/SensorCharts.jsx";
import SensorOverview from "./components/SensorOverview.jsx";
import StatusCard from "./components/StatusCard.jsx";
import { getAlerts, getLatestTelemetry, getTelemetryHistory } from "./api.js";

const STATUS_TONES = {
  SAFE: "safe",
  WATER_DETECTED: "warning",
  WATER_RISING: "danger",
  DRY_RETURNING_TO_SLEEP: "neutral",
  ERROR_SENSOR_READING: "danger",
};

function cardValue(value, suffix = "") {
  if (value === undefined || value === null) return "No data";
  return `${Number(value).toFixed(2)}${suffix}`;
}

export default function App() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");
  const [lastRefresh, setLastRefresh] = useState(null);

  async function refreshData() {
    try {
      const [latestResult, historyResult, alertsResult] = await Promise.allSettled([
        getLatestTelemetry(),
        getTelemetryHistory(50),
        getAlerts(50),
      ]);

      if (latestResult.status === "fulfilled") {
        setLatest(latestResult.value);
      }
      if (historyResult.status === "fulfilled") {
        setHistory(historyResult.value);
      }
      if (alertsResult.status === "fulfilled") {
        setAlerts(alertsResult.value);
      }

      const rejected = [latestResult, historyResult, alertsResult].find((result) => result.status === "rejected");
      setError(rejected ? "Waiting for backend telemetry." : "");
      setLastRefresh(new Date());
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refreshData();
    const intervalId = window.setInterval(refreshData, 3000);
    return () => window.clearInterval(intervalId);
  }, []);

  const statusTone = useMemo(() => STATUS_TONES[latest?.system_status] || "neutral", [latest]);

  return (
    <main className="app-shell">
      <header className="top-bar">
        <div>
          <p className="eyebrow">Residential IoT Flood Monitoring</p>
          <h1>Smart Flood Sentinel</h1>
        </div>
        <div className="refresh-pill">
          <Activity size={16} />
          <span>{lastRefresh ? lastRefresh.toLocaleTimeString() : "Connecting"}</span>
        </div>
      </header>

      {error ? <div className="notice">{error}</div> : null}

      <section className="status-grid" aria-label="Status overview">
        <StatusCard
          title="System Status"
          value={latest?.system_status || "No recent data"}
          tone={statusTone}
          detail={latest?.device_id || "Start backend and send telemetry"}
          icon={Power}
        />
        <StatusCard
          title="Water Sensor"
          value={latest?.water_detected ? "Detected" : latest ? "Dry" : "No data"}
          tone={latest?.water_detected ? "warning" : "safe"}
          detail="Direct leak sensor"
          icon={Droplets}
        />
        <StatusCard
          title="Water Level"
          value={cardValue(latest?.water_level_cm, " cm")}
          tone={latest?.water_rising ? "danger" : "neutral"}
          detail="Calculated from install height"
          icon={Gauge}
        />
        <StatusCard
          title="Distance"
          value={cardValue(latest?.measured_distance_cm, " cm")}
          tone="neutral"
          detail="Ultrasonic reading"
          icon={Ruler}
        />
        <StatusCard
          title="Water Rising"
          value={latest?.water_rising ? "Yes" : latest ? "No" : "No data"}
          tone={latest?.water_rising ? "danger" : "safe"}
          detail="Compared to previous level"
          icon={Activity}
        />
        <StatusCard
          title="Power Mode"
          value={latest?.power_mode || "USB_OR_BATTERY"}
          tone="neutral"
          detail="FireBeetle USB/battery path"
          icon={BatteryCharging}
        />
      </section>

      <section className="content-grid">
        <SensorOverview latest={latest} />
        <SensorCharts history={history} />
      </section>

      <AlertHistory alerts={alerts} />
    </main>
  );
}

