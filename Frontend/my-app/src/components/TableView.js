function TableView({ data }) {
  if (!data.length) return null;

  const [headers, ...rows] = data;

  return (
    <div className="table-section">
      <p className="section-title">Fetched Table Data</p>
      <table className="data-table">
        <thead>
          <tr>{headers.map((h, i) => <th key={i}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => <td key={j}>{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TableView;
