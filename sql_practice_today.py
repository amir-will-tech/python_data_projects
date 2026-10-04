import sqlite3
import pandas as pd

# 1. Connect to local database
conn = sqlite3.connect("supply_chain_v2.db")
cursor = conn.cursor()

# 2. Reset and build relational tables
cursor.execute("DROP TABLE IF EXISTS warehouses;")
cursor.execute("DROP TABLE IF EXISTS shipments;")

cursor.execute("""
CREATE TABLE warehouses (
    warehouse_id INTEGER PRIMARY KEY,
    city TEXT,
    capacity_pallets INTEGER
);
""")

cursor.execute("""
CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY,
    item_description TEXT,
    weight_kg REAL,
    warehouse_id INTEGER
);
""")

# 3. Populate Warehouses
warehouses_data = [
    (1, "Erfurt Hub", 5000),
    (2, "Apolda Depot", 1200),
    (3, "Leipzig Logistics Center", 8000)
]
cursor.executemany("INSERT INTO warehouses VALUES (?, ?, ?);", warehouses_data)

# 4. Populate Shipments (Shipment #1004 has NO warehouse assigned -> None)
shipments_data = [
    (1001, "Hydraulic Oil Drums", 1200.5, 1),
    (1002, "Packaging Straps", 350.0, 2),
    (1003, "Conveyor Spare Parts", 85.0, 1),
    (1004, "Unprocessed Return Goods", 540.0, None)
]
cursor.executemany("INSERT INTO shipments VALUES (?, ?, ?, ?);", shipments_data)
conn.commit()

# -------------------------------------------------------------
# REPORT 1: LEFT JOIN (Unassigned Shipment Audit)
# -------------------------------------------------------------
sql_left_join = """
SELECT 
    shipments.shipment_id,
    shipments.item_description,
    shipments.weight_kg,
    warehouses.city AS destination_city
FROM shipments
LEFT JOIN warehouses 
    ON shipments.warehouse_id = warehouses.warehouse_id;
"""

df_audit = pd.read_sql_query(sql_left_join, conn)

print("\n=======================================================")
print("  REPORT 1: LOGISTICS AUDIT (LEFT JOIN)                ")
print("=======================================================")
print(df_audit)

# -------------------------------------------------------------
# REPORT 2: GROUP BY + HAVING (Heavy Freight Filter > 1000 kg)
# -------------------------------------------------------------
sql_having = """
SELECT 
    warehouses.city,
    COUNT(shipments.shipment_id) AS total_shipments,
    SUM(shipments.weight_kg) AS total_weight_kg
FROM shipments
INNER JOIN warehouses ON shipments.warehouse_id = warehouses.warehouse_id
GROUP BY warehouses.city
HAVING SUM(shipments.weight_kg) > 1000;
"""

df_heavy_freight = pd.read_sql_query(sql_having, conn)

print("\n=======================================================")
print("  REPORT 2: HEAVY FREIGHT WAREHOUSES (> 1000 KG)       ")
print("=======================================================")
print(df_heavy_freight)
# -------------------------------------------------------------
# STEP 5: LOAD (Export Automated Reports to CSV)
# -------------------------------------------------------------
df_audit.to_csv("logistics_audit_report.csv", index=False)
df_heavy_freight.to_csv("heavy_freight_report.csv", index=False)

print("\n=======================================================")
print("  ✅ ETL PIPELINE COMPLETE: REPORTS EXPORTED TO CSV    ")
print("=======================================================\n")

conn.close()

conn.close()