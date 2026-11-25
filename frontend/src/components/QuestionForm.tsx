import { FormEvent, useState } from "react";

import type { QueryFormValues } from "@/lib/types";

interface Props {
  onSubmit: (values: QueryFormValues) => void;
  disabled?: boolean;
}

const DEFAULT_VALUES: QueryFormValues = {
  question: "What was total net revenue last month?",
  mode: "manager",
  detail_level: "summary",
  role: "manager",
  store_id: "",
  category: "",
  sku: "",
  start_date: "2026-05-01",
  end_date: "2026-05-31",
};

export function QuestionForm({ onSubmit, disabled }: Props) {
  const [values, setValues] = useState<QueryFormValues>(DEFAULT_VALUES);

  function update<K extends keyof QueryFormValues>(key: K, value: QueryFormValues[K]) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (values.question.trim()) onSubmit({ ...values, question: values.question.trim() });
  }

  return (
    <form className="question-form" onSubmit={handleSubmit}>
      <label htmlFor="question">Ask a business question</label>
      <textarea
        id="question"
        value={values.question}
        onChange={(e) => update("question", e.target.value)}
        rows={3}
        disabled={disabled}
      />

      <div className="filter-grid">
        <label>
          Mode
          <select
            value={values.mode}
            onChange={(e) => update("mode", e.target.value as QueryFormValues["mode"])}
            disabled={disabled}
          >
            <option value="manager">Manager (plain language)</option>
            <option value="analyst">Analyst (technical)</option>
          </select>
        </label>

        <label>
          Detail
          <select
            value={values.detail_level}
            onChange={(e) => update("detail_level", e.target.value as QueryFormValues["detail_level"])}
            disabled={disabled}
          >
            <option value="summary">Summary</option>
            <option value="deep_dive">Deep dive</option>
          </select>
        </label>

        <label>
          Role (RBAC)
          <select
            value={values.role}
            onChange={(e) => update("role", e.target.value as QueryFormValues["role"])}
            disabled={disabled}
          >
            <option value="manager">Manager</option>
            <option value="analyst">Analyst</option>
            <option value="admin">Admin</option>
          </select>
        </label>
      </div>

      <fieldset className="filter-fieldset">
        <legend>Filters</legend>
        <div className="filter-grid">
          <label>
            Start date
            <input
              type="date"
              value={values.start_date}
              onChange={(e) => update("start_date", e.target.value)}
              disabled={disabled}
            />
          </label>
          <label>
            End date
            <input
              type="date"
              value={values.end_date}
              onChange={(e) => update("end_date", e.target.value)}
              disabled={disabled}
            />
          </label>
          <label>
            Store
            <input
              type="text"
              placeholder="store-a"
              value={values.store_id}
              onChange={(e) => update("store_id", e.target.value)}
              disabled={disabled}
            />
          </label>
          <label>
            Category
            <input
              type="text"
              placeholder="Shoes"
              value={values.category}
              onChange={(e) => update("category", e.target.value)}
              disabled={disabled}
            />
          </label>
          <label>
            SKU
            <input
              type="text"
              placeholder="SHOE-001"
              value={values.sku}
              onChange={(e) => update("sku", e.target.value)}
              disabled={disabled}
            />
          </label>
        </div>
      </fieldset>

      <button type="submit" disabled={disabled}>
        Ask Analyst
      </button>
    </form>
  );
}
