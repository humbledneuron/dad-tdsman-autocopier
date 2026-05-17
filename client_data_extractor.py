import pandas as pd
import json

# Read the Excel file
# Replace 'input.xlsx' with your actual file name
df = pd.read_excel("CLIENT DETAILS.xlsx", dtype=str)

# Replace NaN values with empty strings
df = df.fillna("")

# Create the JSON structure
result = {}

for _, row in df.iterrows():
    name = str(row["SCHOOL NAME"]).strip()

    result[name] = {
        "tan": row["TAN NO"],
        "ain": row["AIN"],
        "itEfilingUname": row["IT EFILING USERNAME"],
        "itEfilingPword": row["IT EFILING PW"],
        "itTracesUname": row["IT TRACES  USERNAME"],
        "itTracesPword": row["IT TRACES ITT PW"],
    }

# Save to JSON file
with open("output.json", "w") as f:
    json.dump(result, f, indent=4)

print("✅ JSON file created: output.json")



##########   PASTE THIS FOR AI TO MODIFY ABOVE CODE      ###################
# import pandas as pd
# import json

# # Read Excel file
# df = pd.read_excel("input.xlsx", dtype=str)

# # Replace NaN with empty string
# df = df.fillna("")

# # Create JSON structure
# result = {}

# for _, row in df.iterrows():
#     name = row["NAME"].strip()

#     result[name] = {
#         "tn": row["TN"],
#         "an": row["AN"],
#         "efun": row["EFUN"],
#         "efpd": row["EFPD"],
#         "ittun": row["ITTUN"],
#         "ittpd": row["ITTPD"],
#     }

# # Save JSON
# with open("output.json", "w") as f:
#     json.dump(result, f, indent=4)

# print("✅ JSON file created successfully!")