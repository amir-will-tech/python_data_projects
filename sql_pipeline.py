import sqlite3
import pandas as pd
# 1. Connect to local SQLite database file (creates it if it doesn't exist)
conn = sqlite3.connect("supply_chain.db")
cursor = conn.cursor()
# 2. Create a SQL Table for Warehouse Stock
cursor.execute("""
CREATE TABLE IF NOT EXISTS warehouse_stock (
item_id INTEGER PRIMARY KEY,
item_name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER,
    unit_cost REAL,
    location TEXT
);
""")

# 3. Clear old sample data and insert fresh logistics rows
cursor.execute("DELETE FROM warehouse_stock;")

sample_inventory = [
    (101, "Heavy Duty Pallet Jack", "Equipment", 8, 450.00, "Erfurt-Hub"),
    (102, "Standard Wooden Pallet", "Packaging", 1200, 15.50, "Dornburg-WH1"),
    (103, "Barcode Scanner Handheld", "Electronics", 15, 220.00, "Erfurt-Hub"),
    (104, "Cardboard Boxes (Large)", "Packaging", 850, 1.25, "Dornburg-WH1"),
    (105, "Stretch Wrap Roll", "Packaging", 45, 8.50, "Apolda-WH2"),
    (106, "Electric Forklift Unit", "Equipment", 2, 18500.00, "Erfurt-Hub"),
    (107, "Safety Boots (Size 43)", "PPE", 12, 65.00, "Apolda-WH2"),
    (108, "High-Vis Vest", "PPE", 80, 12.00, "Dornburg-WH1")
]

cursor.executemany("""
INSERT INTO warehouse_stock VALUES (?, ?, ?, ?, ?, ?);
""", sample_inventory)

conn.commit()
print("✅ Local SQL Database initialized with warehouse stock data!")

# -------------------------------------------------------------
# 4. QUERY 1: Pure SQL - Select Low-Stock Items (Quantity < 50)
# -------------------------------------------------------------
sql_query_low_stock = """
SELECT item_id, item_name, quantity, location
FROM warehouse_stock
WHERE quantity < 50
ORDER BY quantity ASC;
"""

print("\n--- [SQL QUERY 1: Low Stock Warning (< 50 items)] ---")
cursor.execute(sql_query_low_stock)
low_stock_items = cursor.fetchall()
for row in low_stock_items:
    print(f"Item #{row[0]} | {row[1]} | Qty: {row[2]} | Location: {row[3]}")

# -------------------------------------------------------------
# 5. QUERY 2: SQL + Pandas Bridge - Inventory Value by Location
# -------------------------------------------------------------
sql_query_inventory_value = """
SELECT 
    location,
    COUNT(item_id) AS total_distinct_items,
    SUM(quantity) AS total_units,
    ROUND(SUM(quantity * unit_cost), 2) AS total_inventory_value_eur
FROM warehouse_stock
GROUP BY location
ORDER BY total_inventory_value_eur DESC;
"""

# Pull SQL query output DIRECTLY into a Pandas DataFrame!
df_inventory_summary = pd.read_sql_query(sql_query_inventory_value, conn)

print("\n--- [SQL QUERY 2: Aggregated Value by Location (Loaded into Pandas)] ---")
print(df_inventory_summary)

# Close database connection
conn.close()