from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE employees(
 emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    department_id INT,
    salary INT,
    joining_date DATE
);
""")

conn.commit()
cur.close()
conn.close()

print("Table created successfully!")