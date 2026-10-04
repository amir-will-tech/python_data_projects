import pandas as pd
import numpy as np

# 1. EXTRACT: Loading "Dirty" Supply Chain Data
# Imagine this came from a broken CSV file or manual Excel entry
raw_data = {
    "tracking_id": ["TRX-001", "TRX-002", "TRX-002", "TRX-003", "TRX-004"], 
    "dispatch_date": ["2026-10-01", "2026-10-02", "2026-10-02", "URGENT!", "2026-10-04"], 
    "weight_kg": [120.5, 85.0, 85.0, np.nan, 450.2], 
    "destination": ["Berlin", "Munich", "Munich", "Hamburg", "erfurt"] 
}

df = pd.DataFrame(raw_data)

print("=========================================")
print(" ❌ THE RAW, DIRTY DATA")
print("=========================================")
print(df)
print("\nNotice the problems: Duplicate TRX-002, 'URGENT!' is not a date, NaN weight, and 'erfurt' is lowercase.\n")


# 2. TRANSFORM: The Cleaning Pipeline
print("🧹 Running Pandas Cleaning Pipeline...\n")

# A. Remove Duplicate Scans (The double-beep on the scanner)
df_clean = df.drop_duplicates()

# B. Fix Broken Dates (Forces text like "URGENT!" to become NaT - Not a Time)
df_clean['dispatch_date'] = pd.to_datetime(df_clean['dispatch_date'], errors='coerce')

# C. Handle Missing Weights (Fills blank NaN spaces with a safe 0.0)
df_clean['weight_kg'] = df_clean['weight_kg'].fillna(0.0)

# D. Standardize Text Formatting (Capitalizes city names)
df_clean['destination'] = df_clean['destination'].str.title()

# ... (Keep your previous cleaning code above this)

# E. ENRICHMENT: Calculate Shipping Costs
# Let's say the logistics carrier charges €2.50 per kg, plus a €15 base fee per shipment.
df_clean['shipping_cost_eur'] = (df_clean['weight_kg'] * 2.50) + 15.00

# F. ENRICHMENT: Flag Unshippable Freight
# If a dispatch date is missing (NaT) or weight is 0.0, we flag it for manual review.
# We use numpy (np.where) to create a simple True/False conditional column.
df_clean['needs_review'] = np.where(
    df_clean['dispatch_date'].isna() | (df_clean['weight_kg'] == 0.0), 
    "YES", 
    "No"
)

# 3. LOAD: The Final Output
print("=========================================")
print(" ✅ THE CLEANED, PRODUCTION-READY DATA")
print("=========================================")
print(df_clean)