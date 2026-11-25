import Head from "next/head";
import Link from "next/link";
import { useState } from "react";

import { AnswerPanel } from "@/components/AnswerPanel";
import { ErrorBanner } from "@/components/ErrorBanner";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { QuestionForm } from "@/components/QuestionForm";
import { askQuestion, buildQueryRequest, fetchHealth, type QueryFormValues } from "@/lib/apiClient";
import type { HealthStatus, QueryResponse } from "@/lib/types";

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [answer, setAnswer] = useState<QueryResponse | null>(null);
  const [queryId, setQueryId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function checkHealth() {
    try {
      setHealth(await fetchHealth());
    } catch {
      setHealth(null);
    }
  }

  async function handleSubmit(values: QueryFormValues) {
    setLoading(true);
    setError(null);
    try {
      const request = buildQueryRequest(values);
      const result = await askQuestion(request);
      setAnswer(result);
      setQueryId(`${Date.now()}-${request.question.slice(0, 24)}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setAnswer(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head>
        <title>RAG Retail Analyst</title>
      </Head>
      <main className="container">
        <header className="site-header">
          <div>
            <h1>RAG Retail Analyst</h1>
            <p className="subtitle">Inventory &amp; sales intelligence with evidence-linked answers</p>
          </div>
          <nav className="nav-links">
            <Link href="/">Analyst</Link>
            <Link href="/admin">Admin</Link>
          </nav>
        </header>

        <div className="toolbar">
          <button type="button" className="link-btn" onClick={checkHealth}>
            Check API health
          </button>
          {health && (
            <span className="health">
              API: {health.status} ({health.app_env})
            </span>
          )}
        </div>

        <QuestionForm onSubmit={handleSubmit} disabled={loading} />
        {loading && <LoadingSpinner />}
        {error && <ErrorBanner message={error} />}
        {answer && <AnswerPanel response={answer} queryId={queryId} />}
      </main>
    </>
  );
}
