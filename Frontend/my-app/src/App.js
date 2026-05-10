import { useState } from "react";
import UrlInput from "./components/UrlInput";
import TableView from "./components/TableView";
import QueryInput from "./components/QueryInput";
import ResultView from "./components/ResultView";
import EmployeesView from "./components/EmployeesView";
import SalariesView from "./components/SalariesView";
import LeavesView from "./components/LeavesView";
import DBConnect from "./components/DBConnect";
import "./App.css";

function App() {
  const [data, setData] = useState([]);
  const [result, setResult] = useState("");
  const [dbResult, setDbResult] = useState(null);
  const [dbConnected, setDbConnected] = useState(false);

  return (
    <div className="app">
      <div className="app-header">
        <h1 className="app-title">NLP → SQL Generator</h1>
        <span className={`db-badge ${dbConnected ? "db-ok" : "db-fail"}`}>
          {dbConnected ? "DB Connected ✅" : "DB Disconnected ❌"}
        </span>
      </div>

      <DBConnect setDbConnected={setDbConnected} />

      {dbConnected && (
        <>
          <EmployeesView />
          <SalariesView />
          <LeavesView />
          <QueryInput setResult={setResult} setDbResult={setDbResult} />
          <ResultView result={result} dbResult={dbResult} />
        </>
      )}

      <UrlInput setData={setData} />
      <TableView data={data} />
    </div>
  );
}

export default App;
