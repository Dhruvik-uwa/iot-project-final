export default function StatusCard({ title, value, tone = "neutral", detail, icon: Icon }) {
  return (
    <section className={`status-card tone-${tone}`}>
      <div className="status-card-header">
        <span>{title}</span>
        {Icon ? <Icon aria-hidden="true" size={18} /> : null}
      </div>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </section>
  );
}

