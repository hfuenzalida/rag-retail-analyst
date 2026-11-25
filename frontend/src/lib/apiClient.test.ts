import { describe, expect, it } from "vitest";

import { buildQueryRequest } from "@/lib/apiClient";
import type { QueryFormValues } from "@/lib/types";

describe("buildQueryRequest", () => {
  it("maps form values to API payload", () => {
    const values: QueryFormValues = {
      question: "Revenue?",
      mode: "analyst",
      detail_level: "deep_dive",
      role: "analyst",
      store_id: "store-a",
      category: "",
      sku: "",
      start_date: "2026-05-01",
      end_date: "2026-05-31",
    };
    const req = buildQueryRequest(values);
    expect(req.mode).toBe("analyst");
    expect(req.filters?.store_id).toBe("store-a");
    expect(req.filters?.date_range?.start_date).toBe("2026-05-01");
  });
});
