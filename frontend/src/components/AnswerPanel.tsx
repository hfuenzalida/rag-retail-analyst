import { useState } from "react";

import type { QueryResponse } from "@/lib/types";
import { ActionsList } from "./ActionsList";
import { CitationsList } from "./CitationsList";
import { DriversTable } from "./DriversTable";
import { FeedbackControls } from "./FeedbackControls";
import { MetricsTable } from "./MetricsTable";

interface Props {
  response: QueryResponse;
  queryId: string;
}

export function AnswerPanel({ response, queryId }: Props) {
  const [showEvidence, setShowEvidence] = useState(false);

  return (
    <section className="panel answer-panel">
      <header className="panel-header">
        <h2>Answer</h2>
        <div className="badges">
          <span className="badge badge-neutral">{response.routing_decision}</span>
          <span className="badge badge-neutral">{Math.round(response.confidence * 100)}% confidence</span>
        </div>
      </header>

      <p className="summary">{response.summary}</p>

      {response.error && (
        <div className="error-inline-block" role="alert">
          <strong>[{response.error.code}]</strong> {response.error.message}
          {response.error.retry_hint && <p className="meta">{response.error.retry_hint}</p>}
        </div>
      )}

      <MetricsTable metrics={response.metrics} />
      <DriversTable drivers={response.drivers} />
      <ActionsList actions={response.recommendations} />
      <CitationsList citations={response.citations} expanded={showEvidence} />

      <div className="panel-actions">
        <button type="button" className="secondary-btn" onClick={() => setShowEvidence((v) => !v)}>
          {showEvidence ? "Hide data behind this" : "Show data behind this"}
        </button>
      </div>

      <FeedbackControls queryId={queryId} />
    </section>
  );
}
