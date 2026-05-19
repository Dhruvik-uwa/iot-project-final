export default function AlertHistory({ alerts }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Alert History</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Device</th>
              <th>Alert Type</th>
              <th>Message</th>
              <th>Water Level</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr>
                <td colSpan="5" className="empty-cell">No alerts recorded yet.</td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr key={alert.id}>
                  <td>{new Date(alert.timestamp).toLocaleString()}</td>
                  <td>{alert.device_id}</td>
                  <td><span className="alert-type">{alert.alert_type}</span></td>
                  <td>{alert.message}</td>
                  <td>{Number(alert.water_level_cm).toFixed(2)} cm</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

