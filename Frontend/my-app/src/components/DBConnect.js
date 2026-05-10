import { useState } from "react";
import { checkDBStatus } from "../services/api";

function DBConnect({ setDbConnected }) {
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    setStatus("");
    const res = await checkDBStatus();
    if (res.message) {
      setStatus("✅ " + res.message);
      setConnected(true);
      setDbConnected(true);
    } else {
      setStatus("❌ " + (res.error || "Connection failed"));
      setConnected(false);
      setDbConnected(false);
    }
    setLoading(false);
  };

  return (
    <div className="input-section">
      <label>Database Connection</label>
      <div className="input-row">
        <input
          type="text"
          value="postgresql://postgres@127.0.0.1:5432/employees_db"
          readOnly
          style={{ color: "#64748b", cursor: "default" }}
        />
        <button
          className={`btn ${connected ? "btn-secondary" : "btn-primary"}`}
          onClick={handleConnect}
          disabled={loading}
        >
          {loading ? "Connecting..." : connected ? "Reconnect" : "Connect DB"}
        </button>
      </div>
      {status && (
        <p className={connected ? "db-status-ok" : "input-error"} style={{ marginTop: "8px" }}>
          {status}
        </p>
      )}
    </div>
  );
}

export default DBConnect;
