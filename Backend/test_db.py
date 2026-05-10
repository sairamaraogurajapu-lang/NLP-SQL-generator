from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT * FROM employees")
rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()