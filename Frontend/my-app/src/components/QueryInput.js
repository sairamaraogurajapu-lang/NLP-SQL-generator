import { useState } from "react";
import { runNLPQuery } from "../services/api";

function QueryInput({ setResult, setDbResult }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult("");
    setDbResult(null);
    const res = await runNLPQuery(query);
    setResult(res.sql || "");
    setDbResult(res.error ? { error: res.error } : { result: res.result || [] });
    setLoading(false);
  };

  return (
    <div className="input-section">
      <label>Natural Language Query</label>
      <div className="input-row">
        <input
          placeholder="e.g. show all employees, count employees by department..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleRun()}
        />
        <button className="btn btn-secondary" onClick={handleRun} disabled={loading}>
          {loading ? "Running..." : "Run"}
        </button>
      </div>
    </div>
  );
}

export default QueryInput;
