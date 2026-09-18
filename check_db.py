import sqlite3

conn = sqlite3.connect("backend/products.db")
cursor = conn.cursor()

# cursor.execute("""
# SELECT * FROM payment_profiles;
# """)

# cursor.execute("""
# SELECT * FROM order_items;
# """)

cursor.execute("""
SELECT * FROM order_groups;
""")


for row in cursor.fetchall():
    print(row)

conn.close()