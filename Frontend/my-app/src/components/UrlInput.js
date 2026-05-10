import { useState } from "react";
import { fetchTableData } from "../services/api";

function UrlInput({ setData }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFetch = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    const res = await fetchTableData(url);
    if (res.error) {
      setError(res.error);
      setData([]);
    } else {
      setData(res.tableData || []);
    }
    setLoading(false);
  };

  return (
    <div className="input-section">
      <label>Website URL</label>
      <div className="input-row">
        <input
          type="text"
          placeholder="https://example.com/table"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleFetch()}
        />
        <button className="btn btn-primary" onClick={handleFetch} disabled={loading}>
          {loading ? "Fetching..." : "Fetch"}
        </button>
      </div>
      {error && <p className="input-error">{error}</p>}
    </div>
  );
}

export default UrlInput;
