import { useState } from "react";

interface Props {
  queryId: string;
}

type Feedback = "up" | "down" | null;

export function FeedbackControls({ queryId }: Props) {
  const [feedback, setFeedback] = useState<Feedback>(null);
  const [flagged, setFlagged] = useState(false);

  function record(value: Feedback) {
    setFeedback(value);
    const entry = { queryId, value, flagged, at: new Date().toISOString() };
    try {
      const existing = JSON.parse(localStorage.getItem("analyst-feedback") ?? "[]");
      existing.push(entry);
      localStorage.setItem("analyst-feedback", JSON.stringify(existing.slice(-50)));
    } catch {
      // ignore storage errors
    }
  }

  return (
    <div className="feedback-row">
      <span className="meta">Was this answer helpful?</span>
      <button
        type="button"
        className={`chip ${feedback === "up" ? "chip-active" : ""}`}
        onClick={() => record("up")}
        aria-pressed={feedback === "up"}
      >
        👍 Helpful
      </button>
      <button
        type="button"
        className={`chip ${feedback === "down" ? "chip-active" : ""}`}
        onClick={() => record("down")}
        aria-pressed={feedback === "down"}
      >
        👎 Not helpful
      </button>
      <button
        type="button"
        className={`chip ${flagged ? "chip-active" : ""}`}
        onClick={() => setFlagged((v) => !v)}
      >
        Flag issue
      </button>
    </div>
  );
}
