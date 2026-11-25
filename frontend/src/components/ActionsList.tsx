import type { Action } from "@/lib/types";

interface Props {
  actions: Action[];
}

const PRIORITY_CLASS: Record<Action["priority"], string> = {
  high: "badge-high",
  medium: "badge-medium",
  low: "badge-low",
};

export function ActionsList({ actions }: Props) {
  if (actions.length === 0) return null;

  return (
    <section className="section-block">
      <h3>Recommended actions</h3>
      <ul className="action-list">
        {actions.map((action) => (
          <li key={action.label}>
            <div className="action-header">
              <strong>{action.label}</strong>
              <span className={`badge ${PRIORITY_CLASS[action.priority]}`}>{action.priority}</span>
            </div>
            <p>{action.description}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
