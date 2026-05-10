from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from nlp import get_sql
from db import get_connection

app = FastAPI(title="NLP + Web Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Request Models
# -------------------------------
class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    text: str

class SQLRequest(BaseModel):
    sql: str


# -------------------------------
# Shared DB execution helper
# -------------------------------
def run_sql(sql: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        conn.commit()
        return []
    finally:
        cursor.close()
        conn.close()


# -------------------------------
# SSRF guard
# -------------------------------
ALLOWED_SCHEMES = {"http", "https"}

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    hostname = parsed.hostname or ""
    blocked = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
    if hostname in blocked or hostname.startswith("169.254") or hostname.startswith("10.") or hostname.startswith("192.168."):
        return False
    return True


# -------------------------------
# Route 1: Fetch Table Data (Web Scraping)
# -------------------------------
@app.post("/fetch")
def fetch_data(req: URLRequest):
    if not is_safe_url(req.url):
        raise HTTPException(status_code=400, detail="URL not allowed")
    try:
        response = requests.get(req.url, timeout=10)
        if response.status_code != 200:
            return {"error": "Unable to fetch URL"}
        soup = BeautifulSoup(response.text, "html.parser")
        table_data = []
        for row in soup.find_all("tr"):
            cols = row.find_all(["td", "th"])
            row_data = [col.get_text(strip=True) for col in cols]
            if row_data:
                table_data.append(row_data)
        return {"status": "success", "rows": len(table_data), "tableData": table_data}
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# Route 2: NLP → SQL (generate only)
# -------------------------------
@app.post("/query")
def generate_sql(req: QueryRequest):
    if not req.text.strip():
        return {"error": "Query text is required"}
    try:
        sql = get_sql(req.text)
        return {"status": "success", "input": req.text, "sql": sql}
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# Route 3: Execute raw SQL
# -------------------------------
ALLOWED_SQL_PREFIXES = ("select", "with", "alter", "insert", "update", "delete")

@app.post("/execute")
def execute_query(req: SQLRequest):
    if not req.sql.strip().lower().startswith(ALLOWED_SQL_PREFIXES):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    try:
        result = run_sql(req.sql)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# Route 4: NLP → SQL → Execute
# -------------------------------
@app.post("/run")
def run_query(req: QueryRequest):
    if not req.text.strip():
        return {"error": "Query text is required"}
    sql = None
    try:
        sql = get_sql(req.text)
        result = run_sql(sql)
        msg = "Query executed successfully" if sql.strip().lower().startswith(("alter", "insert", "update", "delete")) else None
        return {"status": "success", "input": req.text, "sql": sql, "result": result, "message": msg}
    except Exception as e:
        return {"error": str(e), "sql": sql}


# -------------------------------
# Route 5: Get all employees
# -------------------------------
@app.get("/employees")
def get_employees():
    try:
        result = run_sql("SELECT * FROM employees")
        return {"status": "success", "data": result}
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# Route 6: Get all salaries
# -------------------------------
@app.get("/salaries")
def get_salaries():
    try:
        result = run_sql("SELECT * FROM salaries")
        return {"status": "success", "data": result}
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# Route 7: Get all leaves
# -------------------------------
@app.get("/leaves")
def get_leaves():
    try:
        result = run_sql("SELECT * FROM leaves")
        return {"status": "success", "data": result}
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# Route 8: Test DB connection
# -------------------------------
@app.get("/")
def test_db():
    try:
        conn = get_connection()
        conn.close()
        return {"message": "DB Connected ✅"}
    except Exception as e:
        return {"error": str(e)}


app.mount("/files", StaticFiles(directory="files"), name="files")
