export type Role = "manager" | "analyst" | "admin";
export type DetailLevel = "summary" | "deep_dive";
export type Mode = "manager" | "analyst";
export type TableName = "sales" | "inventory" | "products";

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface QueryFilters {
  date_range?: DateRange;
  store_id?: string;
  category?: string;
  sku?: string;
}

export interface QueryRequest {
  question: string;
  client_id: string;
  role: Role;
  mode: Mode;
  detail_level: DetailLevel;
  filters?: QueryFilters;
  routing_hint?: "local_only" | "hybrid" | "cloud_assist";
}

export interface Metric {
  name: string;
  value: string | number;
  unit?: string;
  time_window?: DateRange;
  context?: string;
}

export interface Driver {
  dimension: string;
  impact: string | number;
  description: string;
}

export interface Action {
  label: string;
  description: string;
  priority: "low" | "medium" | "high";
  type: "inventory" | "pricing" | "promotion" | "other";
}

export interface Citation {
  type: "data" | "document";
  source: string;
  reference: string;
}

export interface ErrorInfo {
  code: string;
  message: string;
  retry_hint?: string;
}

export interface QueryResponse {
  summary: string;
  metrics: Metric[];
  drivers: Driver[];
  recommendations: Action[];
  citations: Citation[];
  confidence: number;
  routing_decision: string;
  error?: ErrorInfo;
}

export interface HealthStatus {
  status: string;
  app_env: string;
  app_name: string;
}

export interface FieldMapping {
  source_column: string;
  target_field: string;
  confidence: number;
  required: boolean;
}

export interface MappingSuggestion {
  client_id: string;
  table_name: TableName;
  mappings: FieldMapping[];
  unmapped_columns: string[];
  missing_required_fields: string[];
  warnings: string[];
}

export interface CsvIngestResponse {
  rows_inserted: number;
  table_name: TableName;
  mapping_status: "proposed" | "confirmed";
}

export interface QueryFormValues {
  question: string;
  mode: Mode;
  detail_level: DetailLevel;
  role: Role;
  store_id: string;
  category: string;
  sku: string;
  start_date: string;
  end_date: string;
}
