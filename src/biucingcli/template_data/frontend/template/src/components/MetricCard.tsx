type MetricCardProps = {
  label: string;
  value: string;
  tone: "amber" | "slate";
};

export function MetricCard({ label, value, tone }: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <p className="metric-card__label">{label}</p>
      <p className="metric-card__value">{value}</p>
    </article>
  );
}
