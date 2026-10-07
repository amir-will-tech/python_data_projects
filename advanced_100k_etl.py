import pandas as pd
import sqlite3

print("🚀 INITIATING ENTERPRISE ETL PIPELINE (100k+ Rows)...\n")

# ==============================================================================
# PHASE 1: EXTRACT
# ==============================================================================
print("⏳ Extracting massive CSV file...")
# We use pandas to read the huge file directly
df_raw = pd.read_csv("RAW_100k_logistics_scans.csv")
print(f"✅ Extraction Complete. Rows loaded: {len(df_raw)}")

# ==============================================================================
# PHASE 2: TRANSFORM
# ==============================================================================
print("⏳ Cleaning 100,000+ rows of data...")

# A. Drop duplicates and copy
df_clean = df_raw.drop_duplicates().copy()

# B. Fix broken dates (SYSTEM_ERROR becomes NaT)
df_clean['scan_date'] = pd.to_datetime(df_clean['scan_date'], errors='coerce')

# C. Fill missing weights with the AVERAGE weight of the whole network
# This is a highly advanced data engineering trick!
average_weight = df_clean['weight_kg'].mean()
df_clean['weight_kg'] = df_clean['weight_kg'].fillna(average_weight)
# Round the weights to 2 decimal places for clean data
df_clean['weight_kg'] = df_clean['weight_kg'].round(2)

print(f"✅ Cleaning Complete. Final clean rows: {len(df_clean)}")

# ==============================================================================
# PHASE 3: BUSINESS LOGIC & LOAD
# ==============================================================================
print("⏳ Processing Business Logic & Loading to Database...")

# Filter for ONLY damaged goods
df_damaged = df_clean[df_clean['status'] == 'Damaged'].copy()

# Connect to a new SQLite database
conn = sqlite3.connect("enterprise_logistics.db")

# Load the entire cleaned DataFrame into SQL automatically!
# Pandas handles the CREATE TABLE and INSERT INTO automatically with .to_sql()
df_clean.to_sql("clean_inventory_scans", conn, if_exists="replace", index=False)
df_damaged.to_sql("damaged_goods_alert", conn, if_exists="replace", index=False)

# Create a grouped summary for the Warehouse Manager
df_damage_summary = df_damaged.groupby('warehouse_location')['tracking_id'].count().reset_index()
df_damage_summary.rename(columns={'tracking_id': 'total_damaged_items'}, inplace=True)

# Export the summary report to CSV
df_damage_summary.to_csv("Damaged_Goods_Summary.csv", index=False)

print("\n=======================================================")
print(" 🚨 WAREHOUSE DAMAGE REPORT SUMMARY                    ")
print("=======================================================")
print(df_damage_summary)

conn.close()
print("\n✅ PIPELINE COMPLETE: 100,000 rows processed, SQL database created, CSV exported.")