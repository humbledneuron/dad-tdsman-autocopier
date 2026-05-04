import csv

file_path = "Z.csv"

last_row = None

# Read the CSV file
with open(file_path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row:  # skip empty rows
            last_row = row

# Get the last column value from the last row
if last_row:
    last_cell_value = last_row[-1]
    print("Last cell value:", last_cell_value)
else:
    print("CSV is empty")