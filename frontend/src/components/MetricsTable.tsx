import type { Metric } from "@/lib/types";

interface Props {
  metrics: Metric[];
}

function formatValue(metric: Metric): string {
  const value = metric.value;
  if (metric.unit === "currency") return `$${Number(value).toLocaleString()}`;
  if (metric.unit === "percent") return `${value}%`;
  return String(value);
}

export function MetricsTable({ metrics }: Props) {
  if (metrics.length === 0) return null;

  return (
    <section className="section-block">
      <h3>Metrics</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              <th>Value</th>
              <th>Window</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => (
              <tr key={m.name}>
                <td>{m.name.replace(/_/g, " ")}</td>
                <td className="numeric">{formatValue(m)}</td>
                <td>
                  {m.time_window
                    ? `${m.time_window.start_date} → ${m.time_window.end_date}`
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
