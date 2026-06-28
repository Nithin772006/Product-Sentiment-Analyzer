function StatCard({ label, value, helper }) {
  return (
    <article className="stat-card">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      {helper ? <span className="stat-helper">{helper}</span> : null}
    </article>
  );
}

export default StatCard;
