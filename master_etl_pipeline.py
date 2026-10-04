import sqlite3
import pandas as pd
import numpy as np

print("🚀 STARTING MASTER ETL PIPELINE...\n")

# ==============================================================================
# PHASE 1: EXTRACT (SQL Relational Database)
# ==============================================================================
print("⏳ [1/3] Extracting data from SQL Database...")

conn = sqlite3.connect("master_logistics.db")
cursor = conn.cursor()

# Reset and create tables
cursor.execute("DROP TABLE IF EXISTS suppliers;")
cursor.execute("DROP TABLE IF EXISTS inventory_scans;")

cursor.execute("""
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT
);
""")

# Intentionally creating a table that allows messy data (TEXT for dates, missing IDs)
cursor.execute("""
CREATE TABLE inventory_scans (
    scan_id INTEGER PRIMARY KEY,
    item_name TEXT,
    scan_date TEXT,
    weight_kg REAL,
    supplier_id INTEGER
);
""")

# Insert Suppliers
cursor.executemany("INSERT INTO suppliers VALUES (?, ?);", [
    (1, "Munich Forklift Co."),
    (2, "Berlin Packaging")
])

# Insert MESSY Inventory Data (Duplicates, Bad Dates, Missing Weights, Missing Suppliers)
messy_data = [
    (101, "Pallet Jack", "2026-10-04", 120.5, 1),
    (102, "cardboard boxes", "2026-10-04", 450.0, 2),
    (103, "cardboard boxes", "2026-10-04", 450.0, 2),  # DUPLICATE!
    (104, "Stretch Wrap", "URGENT_DELIVERY", None, 2), # BAD DATE & MISSING WEIGHT!
    (105, "Unknown Freight", "2026-10-05", 50.0, None) # NO SUPPLIER!
]
cursor.executemany("INSERT INTO inventory_scans VALUES (?, ?, ?, ?, ?);", messy_data)
conn.commit()

# The SQL LEFT JOIN Query to extract everything (Even unassigned freight)
sql_extract = """
SELECT 
    inventory_scans.scan_id,
    inventory_scans.item_name,
    inventory_scans.scan_date,
    inventory_scans.weight_kg,
    suppliers.supplier_name
FROM inventory_scans
LEFT JOIN suppliers 
    ON inventory_scans.supplier_id = suppliers.supplier_id;
"""

# Load raw SQL directly into Pandas
df_raw = pd.read_sql_query(sql_extract, conn)
print("✅ Extraction Complete! Raw Data rows:", len(df_raw))

# ==============================================================================
# PHASE 2: TRANSFORM (Pandas Data Cleaning & Enrichment)
# ==============================================================================
print("⏳ [2/3] Transforming and Cleaning Data in Pandas...")

# A. Remove duplicates AND create a safe, fresh copy to modify
df_clean = df_raw.drop_duplicates().copy()

# B. Standardize Text (Capitalize item names)
df_clean['item_name'] = df_clean['item_name'].str.title()

# C. Fix broken dates (Replaces the text column with a real datetime column)
df_clean['scan_date'] = pd.to_datetime(df_clean['scan_date'], errors='coerce')

# D. Fill missing weights with 0.0
df_clean['weight_kg'] = df_clean['weight_kg'].fillna(0.0)

# E. Handle missing supplier names from the LEFT JOIN
df_clean['supplier_name'] = df_clean['supplier_name'].fillna("UNASSIGNED")

# F. ENRICHMENT: Flag items that need manual review
df_clean['needs_review'] = np.where(
    df_clean['scan_date'].isna() | (df_clean['weight_kg'] == 0.0) | (df_clean['supplier_name'] == "UNASSIGNED"),
    "🚨 YES",
    "✅ No"
)
print("✅ Transformation Complete!")

# ==============================================================================
# PHASE 3: LOAD (Export to Final Report)
# ==============================================================================
print("⏳ [3/3] Loading data into final CSV report...")

# Export to CSV
report_filename = "FINAL_Daily_Inventory_Report.csv"
df_clean.to_csv(report_filename, index=False)

print(f"✅ Load Complete! File saved as: {report_filename}\n")

# Display the final masterpiece in the terminal
print("=============================================================================")
print(" 📊 FINAL AUTOMATED REPORT (Ready for Management)")
print("=============================================================================")
print(df_clean.to_string(index=False))

conn.close()