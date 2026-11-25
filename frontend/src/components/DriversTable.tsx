import type { Driver } from "@/lib/types";

interface Props {
  drivers: Driver[];
}

export function DriversTable({ drivers }: Props) {
  if (drivers.length === 0) return null;

  return (
    <section className="section-block">
      <h3>Drivers</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Dimension</th>
              <th>Impact</th>
              <th>Explanation</th>
            </tr>
          </thead>
          <tbody>
            {drivers.map((d, i) => (
              <tr key={`${d.dimension}-${i}`}>
                <td>{d.dimension}</td>
                <td className={`numeric ${Number(d.impact) < 0 ? "negative" : "positive"}`}>
                  {Number(d.impact).toLocaleString()}
                </td>
                <td>{d.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
