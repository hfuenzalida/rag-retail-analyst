import type { Citation } from "@/lib/types";

interface Props {
  citations: Citation[];
  expanded?: boolean;
}

export function CitationsList({ citations, expanded = false }: Props) {
  if (citations.length === 0) return null;
  const visible = expanded ? citations : citations.slice(0, 3);

  return (
    <section className="section-block">
      <h3>Evidence &amp; citations</h3>
      <ul className="citation-list">
        {visible.map((c, i) => (
          <li key={`${c.reference}-${i}`}>
            <span className="citation-type">{c.type}</span>
            <span className="citation-source">{c.source}</span>
            <code>{c.reference}</code>
          </li>
        ))}
      </ul>
      {!expanded && citations.length > 3 && (
        <p className="meta">{citations.length - 3} more citations available — use “Show data behind this”.</p>
      )}
    </section>
  );
}
