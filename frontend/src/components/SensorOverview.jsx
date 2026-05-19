function displayBool(value) {
  if (value === undefined || value === null) return "No data";
  return value ? "Yes" : "No";
}

function displayNumber(value) {
  if (value === undefined || value === null) return "No data";
  return `${Number(value).toFixed(2)} cm`;
}

export default function SensorOverview({ latest }) {
  const rows = [
    ["Water detected", displayBool(latest?.water_detected)],
    ["Measured distance", displayNumber(latest?.measured_distance_cm)],
    ["Water level", displayNumber(latest?.water_level_cm)],
    ["Last water level", displayNumber(latest?.last_water_level_cm)],
    ["Water rising", displayBool(latest?.water_rising)],
    ["Device ID", latest?.device_id || "No data"],
    ["Timestamp", latest?.timestamp ? new Date(latest.timestamp).toLocaleString() : "No data"],
  ];

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Live Sensor Display</h2>
      </div>
      <div className="sensor-grid">
        {rows.map(([label, value]) => (
          <div className="sensor-row" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

