import Head from "next/head";
import Link from "next/link";
import { FormEvent, useState } from "react";

import { ErrorBanner } from "@/components/ErrorBanner";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { confirmCsvIngest, parseCsv, proposeCsvMapping } from "@/lib/apiClient";
import type { MappingSuggestion, TableName } from "@/lib/types";

export default function AdminPage() {
  const [tableName, setTableName] = useState<TableName>("sales");
  const [file, setFile] = useState<File | null>(null);
  const [csvText, setCsvText] = useState("");
  const [suggestion, setSuggestion] = useState<MappingSuggestion | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handlePropose(e: FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Select a CSV file first.");
      return;
    }
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const text = await file.text();
      setCsvText(text);
      const result = await proposeCsvMapping(file, tableName);
      setSuggestion(result);
      setMessage("Mapping proposal received — review before confirming.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    if (!suggestion || !csvText) return;
    const { headers, rows } = parseCsv(csvText);
    if (suggestion.missing_required_fields.length > 0) {
      setError(`Cannot confirm — missing required fields: ${suggestion.missing_required_fields.join(", ")}`);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await confirmCsvIngest({
        client_id: suggestion.client_id,
        table_name: suggestion.table_name,
        headers,
        rows,
        mappings: suggestion.mappings,
      });
      setMessage(`Loaded ${result.rows_inserted} rows into ${result.table_name} (${result.mapping_status}).`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Confirm failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head>
        <title>Admin — RAG Retail Analyst</title>
      </Head>
      <main className="container">
        <header className="site-header">
          <div>
            <h1>Admin ingestion</h1>
            <p className="subtitle">Upload CSV, review proposed mappings, confirm load (admin only)</p>
          </div>
          <nav className="nav-links">
            <Link href="/">Analyst</Link>
            <Link href="/admin">Admin</Link>
          </nav>
        </header>

        <form className="panel admin-form" onSubmit={handlePropose}>
          <label>
            Target table
            <select value={tableName} onChange={(e) => setTableName(e.target.value as TableName)}>
              <option value="sales">sales</option>
              <option value="inventory">inventory</option>
              <option value="products">products</option>
            </select>
          </label>

          <label>
            CSV file
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>

          <button type="submit" disabled={loading || !file}>
            Propose mapping
          </button>
        </form>

        {loading && <LoadingSpinner />}
        {error && <ErrorBanner message={error} />}
        {message && <p className="success-banner">{message}</p>}

        {suggestion && (
          <section className="panel">
            <h2>Proposed mapping</h2>
            {suggestion.warnings.map((w) => (
              <p key={w} className="meta">
                {w}
              </p>
            ))}

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Source column</th>
                    <th>Target field</th>
                    <th>Confidence</th>
                    <th>Required</th>
                  </tr>
                </thead>
                <tbody>
                  {suggestion.mappings.map((m) => (
                    <tr key={m.source_column}>
                      <td>{m.source_column}</td>
                      <td>{m.target_field}</td>
                      <td>{Math.round(m.confidence * 100)}%</td>
                      <td>{m.required ? "yes" : "no"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {suggestion.missing_required_fields.length > 0 && (
              <p className="error-inline">
                Missing required: {suggestion.missing_required_fields.join(", ")}
              </p>
            )}

            <button
              type="button"
              className="secondary-btn"
              disabled={loading || suggestion.missing_required_fields.length > 0}
              onClick={handleConfirm}
            >
              Confirm and load data
            </button>
          </section>
        )}
      </main>
    </>
  );
}
