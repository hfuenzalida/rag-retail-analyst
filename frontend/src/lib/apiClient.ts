import type {
  CsvIngestResponse,
  HealthStatus,
  MappingSuggestion,
  QueryFormValues,
  QueryRequest,
  QueryResponse,
  TableName,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DEFAULT_CLIENT_ID = "demo-retail";

export type { QueryFormValues, QueryRequest, QueryResponse, MappingSuggestion } from "./types";

export function buildQueryRequest(
  values: QueryFormValues,
  clientId: string = DEFAULT_CLIENT_ID
): QueryRequest {
  const filters =
    values.start_date && values.end_date
      ? {
          date_range: { start_date: values.start_date, end_date: values.end_date },
          store_id: values.store_id || undefined,
          category: values.category || undefined,
          sku: values.sku || undefined,
        }
      : values.store_id || values.category || values.sku
        ? {
            store_id: values.store_id || undefined,
            category: values.category || undefined,
            sku: values.sku || undefined,
          }
        : undefined;

  return {
    question: values.question,
    client_id: clientId,
    role: values.role,
    mode: values.mode,
    detail_level: values.detail_level,
    filters,
  };
}

export async function askQuestion(request: QueryRequest): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_URL}/healthz`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function proposeCsvMapping(
  file: File,
  tableName: TableName,
  clientId: string = DEFAULT_CLIENT_ID
): Promise<MappingSuggestion> {
  const form = new FormData();
  form.append("client_id", clientId);
  form.append("table_name", tableName);
  form.append("file", file);

  const res = await fetch(`${API_URL}/ingest/csv`, {
    method: "POST",
    headers: { "X-Role": "admin" },
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed ${res.status}: ${text}`);
  }
  return res.json();
}

export async function confirmCsvIngest(payload: {
  client_id: string;
  table_name: TableName;
  headers: string[];
  rows: string[][];
  mappings: MappingSuggestion["mappings"];
}): Promise<CsvIngestResponse> {
  const res = await fetch(`${API_URL}/ingest/csv/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Role": "admin" },
    body: JSON.stringify({ ...payload, role: "admin" }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Confirm failed ${res.status}: ${text}`);
  }
  return res.json();
}

export function parseCsv(text: string): { headers: string[]; rows: string[][] } {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  if (lines.length === 0) return { headers: [], rows: [] };
  const headers = lines[0].split(",").map((h) => h.trim());
  const rows = lines.slice(1).map((line) => line.split(",").map((c) => c.trim()));
  return { headers, rows };
}
