function ResultView({ result, dbResult }) {
  const rows = dbResult?.result || [];
  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];

  return (
    <>
      {result && (
        <div className="result-section" style={{ marginBottom: "24px" }}>
          <strong>Generated SQL</strong>
          <pre>{result}</pre>
        </div>
      )}

      {dbResult?.error && (
        <div className="result-section">
          <strong>DB Error</strong>
          <pre className="error-text">{dbResult.error}</pre>
        </div>
      )}

      {dbResult && !dbResult.error && rows.length === 0 && (
        <div className="result-section">
          <strong>Query Results</strong>
          <p className="no-data">
            {dbResult.message || "No records found."}
          </p>
        </div>
      )}

      {rows.length > 0 && (
        <div className="table-section">
          <p className="section-title">Query Results — {rows.length} row{rows.length !== 1 ? "s" : ""}</p>
          <table className="data-table">
            <thead>
              <tr>{columns.map((col, i) => <th key={i}>{col}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {columns.map((col, j) => <td key={j}>{String(row[col] ?? "")}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default ResultView;
