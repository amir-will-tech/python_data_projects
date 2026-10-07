import sqlite3
import random
from datetime import datetime, timedelta

print("⏳ Generating 100,000 rows of messy logistics data... Please wait.")

# 1. Connect to new SQL database
conn = sqlite3.connect("big_logistics.db")
cursor = conn.cursor()

# 2. Build SQL Tables
cursor.execute("DROP TABLE IF EXISTS suppliers;")
cursor.execute("DROP TABLE IF EXISTS global_shipments;")

cursor.execute("""
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT,
    country TEXT
);
""")

cursor.execute("""
CREATE TABLE global_shipments (
    tracking_id TEXT PRIMARY KEY,
    dispatch_date TEXT,
    weight_kg REAL,
    supplier_id INTEGER
);
""")

# 3. Generate 50 Suppliers
suppliers = [(i, f"Vendor_{i}", random.choice(["Germany", "Poland", "Netherlands", "China"])) for i in range(1, 51)]
cursor.executemany("INSERT INTO suppliers VALUES (?, ?, ?);", suppliers)

# 4. Generate 100,000 Shipments
shipments = []
base_date = datetime(2026, 1, 1)

for i in range(1, 100001):
    tracking = f"TRX-{1000000 + i}"
    
    # Introduce dirty data
    dispatch = "PENDING_SYSTEM_ERROR" if random.random() < 0.05 else (base_date + timedelta(days=random.randint(0, 250))).strftime("%Y-%m-%d")
    weight = None if random.random() < 0.10 else round(random.uniform(5.0, 1500.0), 2)
    supplier = None if random.random() < 0.05 else random.randint(1, 50)
    
    shipments.append((tracking, dispatch, weight, supplier))

cursor.executemany("INSERT INTO global_shipments VALUES (?, ?, ?, ?);", shipments)
conn.commit()
conn.close()

print("✅ DONE! Created 'big_logistics.db' SQL Database with 100,000 shipments and 50 suppliers.")