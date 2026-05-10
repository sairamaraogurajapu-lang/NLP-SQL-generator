from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
INSERT INTO employees(emp_id,emp_name,salary,joining_date)
VALUES
(1,'Raja_jagadish',79000, DATE '2017-08-21'),
(2,'Chakravarthi',76000, DATE'2016-07-21'),
(3,'Sairam',44000, DATE'2023-02-01'),
(4,'praveen',47000, DATE'2022-09-14'),
(5,'uday kiran',34000, DATE'2024-02-11'))

conn.commit()
cur.close()
conn.close()

print("Data inserted!")