import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function formatChartData(history) {
  return history.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    waterLevel: Number(item.water_level_cm),
    distance: Number(item.measured_distance_cm),
  }));
}

export default function SensorCharts({ history }) {
  const data = formatChartData(history);

  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <h2>Sensor Charts</h2>
      </div>
      {data.length === 0 ? (
        <div className="empty-chart">No telemetry history yet.</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 10, right: 18, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d9e0ea" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} unit=" cm" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="waterLevel" name="Water level" stroke="#d12f2f" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="distance" name="Ultrasonic distance" stroke="#1d6f8f" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}

