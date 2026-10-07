
import sqlite3
import pandas as pd
import numpy as np

print("🚀 Starting Big Data ETL Pipeline...")

# 1. EXTRACT: Connect and JOIN the 100,000 rows
conn = sqlite3.connect("big_logistics.db")

sql_query = """
SELECT 
    global_shipments.tracking_id,
    global_shipments.dispatch_date,
    global_shipments.weight_kg,
    suppliers.supplier_name,
    suppliers.country
FROM global_shipments
LEFT JOIN suppliers ON global_shipments.supplier_id = suppliers.supplier_id;
"""

print("⏳ Extracting data from database...")
df = pd.read_sql_query(sql_query, conn)

# 2. TRANSFORM: Clean the massive dataset
print("🧹 Cleaning 100,000 rows in Pandas...")

# Fix dates and copy safely
df_clean = df.copy()
df_clean['dispatch_date'] = pd.to_datetime(df_clean['dispatch_date'], errors='coerce')

# Fill missing data
df_clean['weight_kg'] = df_clean['weight_kg'].fillna(0.0)
df_clean['supplier_name'] = df_clean['supplier_name'].fillna("UNKNOWN")
df_clean['country'] = df_clean['country'].fillna("UNKNOWN")

# Apply the Business Logic Flag
df_clean['critical_flag'] = np.where(
    (df_clean['weight_kg'] == 0.0) | (df_clean['country'] == "UNKNOWN"),
    "YES",
    "NO"
)

# 3. LOAD: Export ONLY the critical flagged shipments
print("💾 Filtering and exporting critical report...")
df_critical = df_clean[df_clean['critical_flag'] == "YES"]

df_critical.to_csv("critical_shipments_audit.csv", index=False)

print(f"✅ DONE! Found {len(df_critical)} critical shipments out of {len(df_clean)} total.")
conn.close()