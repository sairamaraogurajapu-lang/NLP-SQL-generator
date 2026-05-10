const BASE_URL = "http://localhost:8000";

export const checkDBStatus = async () => {
  try {
    const res = await fetch(`${BASE_URL}/`);
    return await res.json();
  } catch {
    return { error: "Backend unreachable" };
  }
};

export const fetchTableData = async (url) => {
  try {
    const res = await fetch(`${BASE_URL}/fetch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error("Failed to fetch table data");
    return await res.json();
  } catch (error) {
    return { error: error.message, tableData: [] };
  }
};

export const runNLPQuery = async (text) => {
  try {
    const res = await fetch(`${BASE_URL}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error("Failed to run NLP query");
    return await res.json();
  } catch (error) {
    return { error: error.message };
  }
};

export const executeSQL = async (sql) => {
  try {
    const res = await fetch(`${BASE_URL}/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sql }),
    });
    if (!res.ok) throw new Error("Failed to execute SQL");
    return await res.json();
  } catch (error) {
    return { error: error.message };
  }
};

export const getEmployees = async () => {
  try {
    const res = await fetch(`${BASE_URL}/employees`);
    if (!res.ok) throw new Error("Failed to fetch employees");
    return await res.json();
  } catch (error) {
    return { error: error.message, data: [] };
  }
};

export const getSalaries = async () => {
  try {
    const res = await fetch(`${BASE_URL}/salaries`);
    if (!res.ok) throw new Error("Failed to fetch salaries");
    return await res.json();
  } catch (error) {
    return { error: error.message, data: [] };
  }
};

export const getLeaves = async () => {
  try {
    const res = await fetch(`${BASE_URL}/leaves`);
    if (!res.ok) throw new Error("Failed to fetch leaves");
    return await res.json();
  } catch (error) {
    return { error: error.message, data: [] };
  }
};
