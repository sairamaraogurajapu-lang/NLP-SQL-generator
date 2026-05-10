import { useState } from "react";
import { getEmployees } from "../services/api";

function EmployeesView() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);

  const handleLoad = async () => {
    setLoading(true);
    setError("");
    const res = await getEmployees();
    if (res.error) {
      setError(res.error);
    } else {
      setEmployees(res.data || []);
      setLoaded(true);
    }
    setLoading(false);
  };

  const columns = employees.length > 0 ? Object.keys(employees[0]) : [];

  return (
    <div className="input-section" style={{ marginBottom: "24px" }}>
      <label>Employees Table</label>
      <div className="input-row" style={{ marginBottom: employees.length ? "16px" : "0" }}>
        <button className="btn btn-primary" onClick={handleLoad} disabled={loading}>
          {loading ? "Loading..." : loaded ? "Reload Employees" : "Load Employees"}
        </button>
      </div>

      {error && <p className="input-error">{error}</p>}

      {employees.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <p className="section-title" style={{ marginBottom: "10px" }}>
            {employees.length} employee{employees.length !== 1 ? "s" : ""} found
          </p>
          <table className="data-table">
            <thead>
              <tr>{columns.map((col, i) => <th key={i}>{col}</th>)}</tr>
            </thead>
            <tbody>
              {employees.map((row, i) => (
                <tr key={i}>
                  {columns.map((col, j) => <td key={j}>{String(row[col] ?? "")}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {loaded && employees.length === 0 && !error && (
        <p className="no-data">No employees found.</p>
      )}
    </div>
  );
}

export default EmployeesView;
