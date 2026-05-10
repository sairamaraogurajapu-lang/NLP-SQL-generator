import { useState } from "react";
import { getSalaries } from "../services/api";

function SalariesView() {
  const [salaries, setSalaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);

  const handleLoad = async () => {
    setLoading(true);
    setError("");
    const res = await getSalaries();
    if (res.error) {
      setError(res.error);
    } else {
      setSalaries(res.data || []);
      setLoaded(true);
    }
    setLoading(false);
  };

  const columns = salaries.length > 0 ? Object.keys(salaries[0]) : [];

  return (
    <div className="input-section" style={{ marginBottom: "24px" }}>
      <label>Salaries Table</label>
      <div className="input-row" style={{ marginBottom: salaries.length ? "16px" : "0" }}>
        <button className="btn btn-primary" onClick={handleLoad} disabled={loading}>
          {loading ? "Loading..." : loaded ? "Reload Salaries" : "Load Salaries"}
        </button>
      </div>
      {error && <p className="input-error">{error}</p>}
      {salaries.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <p className="section-title" style={{ marginBottom: "10px" }}>
            {salaries.length} record{salaries.length !== 1 ? "s" : ""} found
          </p>
          <table className="data-table">
            <thead>
              <tr>{columns.map((col, i) => <th key={i}>{col}</th>)}</tr>
            </thead>
            <tbody>
              {salaries.map((row, i) => (
                <tr key={i}>
                  {columns.map((col, j) => <td key={j}>{String(row[col] ?? "")}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {loaded && salaries.length === 0 && !error && (
        <p className="no-data">No salary records found.</p>
      )}
    </div>
  );
}

export default SalariesView;
