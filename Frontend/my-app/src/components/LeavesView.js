import { useState } from "react";
import { getLeaves } from "../services/api";

function LeavesView() {
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);

  const handleLoad = async () => {
    setLoading(true);
    setError("");
    const res = await getLeaves();
    if (res.error) {
      setError(res.error);
    } else {
      setLeaves(res.data || []);
      setLoaded(true);
    }
    setLoading(false);
  };

  const columns = leaves.length > 0 ? Object.keys(leaves[0]) : [];

  return (
    <div className="input-section" style={{ marginBottom: "24px" }}>
      <label>Leaves Table</label>
      <div className="input-row" style={{ marginBottom: leaves.length ? "16px" : "0" }}>
        <button className="btn btn-primary" onClick={handleLoad} disabled={loading}>
          {loading ? "Loading..." : loaded ? "Reload Leaves" : "Load Leaves"}
        </button>
      </div>
      {error && <p className="input-error">{error}</p>}
      {leaves.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <p className="section-title" style={{ marginBottom: "10px" }}>
            {leaves.length} record{leaves.length !== 1 ? "s" : ""} found
          </p>
          <table className="data-table">
            <thead>
              <tr>{columns.map((col, i) => <th key={i}>{col}</th>)}</tr>
            </thead>
            <tbody>
              {leaves.map((row, i) => (
                <tr key={i}>
                  {columns.map((col, j) => <td key={j}>{String(row[col] ?? "")}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {loaded && leaves.length === 0 && !error && (
        <p className="no-data">No leave records found.</p>
      )}
    </div>
  );
}

export default LeavesView;
