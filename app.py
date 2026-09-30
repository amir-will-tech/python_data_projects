import pandas as pd
# Local verification test
data = [
    {"worker": "Mamad", "status": "Local Setup Complete"},
    {"worker": "Alex", "status": "Ready for Week 2"}
]

df = pd.DataFrame(data)

print("\n==========================================")
print("   SUCCESS! LOCAL PYTHON & PANDAS ACTIVE  ")
print("==========================================\n")
print(df)
