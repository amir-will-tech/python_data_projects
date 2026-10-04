import sqlite3
import pandas as pd

# 1. Connect to a new database file
conn = sqlite3.connect("logistics_relational.db")
cursor = conn.cursor()

# 2. CREATE TABLE 1: Suppliers
cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY,
    company_name TEXT,
    contact_email TEXT
);
""")

# 3. CREATE TABLE 2: Inventory (Notice the 'supplier_id' column!)
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    item_id INTEGER PRIMARY KEY,
    item_name TEXT,
    quantity INTEGER,
    supplier_id INTEGER
);
""")

# 4. Clear old data for a fresh run
cursor.execute("DELETE FROM suppliers;")
cursor.execute("DELETE FROM inventory;")

# 5. Insert Supplier Data
suppliers_data = [
    (1, "Munich Forklift Co.", "dispatch@munich-forklift.de"),
    (2, "Berlin Packaging Partners", "orders@berlin-pack.de"),
    (3, "Frankfurt Safety Gear", "b2b@ffm-safety.de")
]
cursor.executemany("INSERT INTO suppliers VALUES (?, ?, ?);", suppliers_data)

# 6. Insert Inventory Data (Linked by supplier_id)
inventory_data = [
    (101, "Electric Pallet Jack", 4, 1),      # Belongs to Supplier 1
    (102, "Cardboard Boxes (L)", 850, 2),     # Belongs to Supplier 2
    (103, "Stretch Wrap Roll", 120, 2),       # Belongs to Supplier 2
    (104, "Steel-Toe Boots", 45, 3)           # Belongs to Supplier 3
]
cursor.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?);", inventory_data)
conn.commit()

# -------------------------------------------------------------
# 7. THE MAGIC: SQL INNER JOIN
# We want the Item Name, the Quantity, AND the Supplier's Name in one report.
# -------------------------------------------------------------
sql_join_query = """
SELECT 
    inventory.item_name, 
    inventory.quantity, 
    suppliers.company_name,
    suppliers.contact_email
FROM inventory
INNER JOIN suppliers 
    ON inventory.supplier_id = suppliers.supplier_id;
"""

# Load the merged data directly into Pandas
df_merged_report = pd.read_sql_query(sql_join_query, conn)

print("\n=======================================================")
print("  SUPPLY CHAIN REORDER REPORT (MULTI-TABLE JOIN)       ")
print("=======================================================\n")
print(df_merged_report)

conn.close()