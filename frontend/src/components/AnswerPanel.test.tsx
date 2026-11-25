import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AnswerPanel } from "@/components/AnswerPanel";
import type { QueryResponse } from "@/lib/types";

const SAMPLE: QueryResponse = {
  summary: "Total revenue was $1,640 in May 2026.",
  metrics: [
    { name: "total_revenue", value: "1640", unit: "currency", time_window: { start_date: "2026-05-01", end_date: "2026-05-31" } },
  ],
  drivers: [{ dimension: "category:Shoes", impact: "-1260", description: "Shoes decreased" }],
  recommendations: [
    { label: "Review reorder points", description: "Stock-out rate elevated.", priority: "high", type: "inventory" },
  ],
  citations: [{ type: "data", source: "sales", reference: "metric:total_revenue" }],
  confidence: 0.9,
  routing_decision: "local_only",
};

describe("AnswerPanel", () => {
  it("renders summary, metrics, drivers, and actions", () => {
    render(<AnswerPanel response={SAMPLE} queryId="test-1" />);
    expect(screen.getByText(/Total revenue was/)).toBeInTheDocument();
    expect(screen.getByText("total revenue")).toBeInTheDocument();
    expect(screen.getByText("Drivers")).toBeInTheDocument();
    expect(screen.getByText("Recommended actions")).toBeInTheDocument();
    expect(screen.getByText("Review reorder points")).toBeInTheDocument();
  });
});
