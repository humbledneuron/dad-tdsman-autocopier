import pandas as pd
import os
import shutil
import warnings
import calendar
import xlrd
import xlwt
from xlutils.copy import copy

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Predefined file paths
csv_file_path = 'February_2025_report.csv'
excel_file_path = 'TDS Q4 24Q2425 ZPHS MOHAMMADAPUR.xls'

def get_last_day_of_month(month_name, year=2025):
    """Get the last day of the given month"""
    try:
        # Convert month name to month number
        month_number = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }[month_name]
        
        # Get the last day of the month
        last_day = calendar.monthrange(year, month_number)[1]
        
        # Format as dd/mm/yyyy
        return f"{last_day:02d}/{month_number:02d}/{year}"
    except KeyError:
        print(f"Warning: Unknown month '{month_name}', using default date")
        return "31/03/2025"  # Default to March 31, 2025

def install_required_libraries():
    """Install required libraries if they're not present"""
    try:
        import xlwt
        import xlutils
    except ImportError:
        print("Installing required libraries...")
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "xlwt", "xlutils"])
        print("Libraries installed successfully.")

def transfer_csv_to_excel():
    """
    Transfer data from CSV file to the 'Employee Details' sheet in Excel file
    """
    # Install required libraries
    install_required_libraries()
    
    # Check if files exist
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' does not exist")
        return False
    
    if not os.path.exists(excel_file_path):
        print(f"Error: Excel file '{excel_file_path}' does not exist")
        return False
    
    # Create a backup of the original Excel file
    backup_file = f"{excel_file_path}.backup"
    try:
        shutil.copy2(excel_file_path, backup_file)
        print(f"Created backup at '{backup_file}'")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    try:
        # Read the CSV file
        csv_df = pd.read_csv(csv_file_path)
        print(f"Successfully read CSV file with {len(csv_df)} rows and {len(csv_df.columns)} columns")
        
        if len(csv_df) == 0:
            print("Warning: CSV file is empty")
            return False
            
        # Open the .xls file with xlrd
        rb = xlrd.open_workbook(excel_file_path, formatting_info=True)
        
        # Find the Employee Details sheet index
        employee_sheet_index = None
        for idx, sheet_name in enumerate(rb.sheet_names()):
            if sheet_name == 'Employee Details':
                employee_sheet_index = idx
                break
                
        if employee_sheet_index is None:
            print("Error: Employee Details sheet not found in the Excel file")
            return False
            
        # Read the Employee Details sheet
        employee_sheet = rb.sheet_by_index(employee_sheet_index)
        print(f"Found Employee Details sheet with {employee_sheet.nrows} rows")
        
        # Get header row (assuming it's the first row)
        header_row = [employee_sheet.cell_value(0, col) for col in range(employee_sheet.ncols)]
        
        # Print all column headers for debugging
        print("Column headers in Excel file:")
        for idx, header in enumerate(header_row):
            print(f"{idx}: {header}")
        
        # Create a writable copy of the workbook
        wb = copy(rb)
        
        # Get the Employee Details sheet in writable format
        ws = wb.get_sheet(employee_sheet_index)
        
        # Define column mappings with possible variations for the column names
        column_mappings = {
            'Employee Serial No (313)': ['Employee Serial No (313)', 'Employee Serial No(313)', 'Employee Serial No'],
            'Challan Serial Reference (301)': ['Challan Serial Reference (301)', 'Challan Serial Reference(301)', 'Challan Serial Reference'],
            'PAN of the Employee (315)': ['PAN of the Employee (315)', 'PAN of the Employee(315)', 'PAN of the Employee'],
            'Name of the Employee (316)': ['Name of the Employee (316)', 'Name of the Employee(316)', 'Name of the Employee'],
            'Section Code (317)': ['Section Code (317)', 'Section Code(317)', 'Section Code'],
            'Payment/Credit Date (dd/mm/yyyy) (318)': ['Payment/Credit Date (dd/mm/yyyy) (318)', 'Payment/Credit Date(dd/mm/yyyy)(318)', 'Payment/Credit Date'],
            'Amount Paid/Credited (320)': ['Amount Paid/Credited (320)', 'Amount Paid/Credited(320)', 'Amount Paid/Credited'],
            'TDS (321)': ['TDS (321)', 'TDS(321)', 'TDS'],
            'Surcharge': ['Surcharge', 'Surcharge ()', 'surcharge'],
            'Education Cess (322)': ['Education Cess (322)', 'Education Cess(322)', 'Education Cess'],
            'Total Tax Deducted (323)': ['Total Tax Deducted (323)', 'Total Tax Deducted(323)', 'Total Tax Deducted'],
            'Total Tax Deposited (324)': ['Total Tax Deposited (324)', 'Total Tax Deposited(324)', 'Total Tax Deposited'],
            'Reason for Non-deduction/Lower Deduction (326)': ['Reason for Non-deduction/Lower Deduction (326)', 'Reason for Non-deduction/Lower Deduction(326)', 'Reason for Non-deduction'],
            'Certificate number for Lower/non deduction (327)': ['Certificate number for Lower/non deduction (327)', 'Certificate number for Lower/non deduction(327)', 'Certificate number']
        }
        
        # Find column indices by checking each possible variation
        column_indices = {}
        for col_key, possible_names in column_mappings.items():
            column_indices[col_key] = None
            for possible_name in possible_names:
                for col_idx, header in enumerate(header_row):
                    if possible_name.lower() in header.lower():
                        column_indices[col_key] = col_idx
                        print(f"Found column '{col_key}' at index {col_idx} with header '{header}'")
                        break
                if column_indices[col_key] is not None:
                    break
        
        # Check if all needed columns were found
        missing_columns = [col for col, idx in column_indices.items() if idx is None]
        if missing_columns:
            print(f"Warning: The following columns were not found: {missing_columns}")
            return False
        
        # Start adding rows after the existing data
        start_row = employee_sheet.nrows
        
        # Add data from CSV
        for row_idx, csv_row in enumerate(csv_df.iterrows()):
            csv_row = csv_row[1]  # Get the actual row data (pandas returns index, row)
            excel_row = start_row + row_idx
            
            # Write data to appropriate columns
            ws.write(excel_row, column_indices['Employee Serial No (313)'], float(csv_row['Sno.']))
            ws.write(excel_row, column_indices['Challan Serial Reference (301)'], csv_row['Month'])
            ws.write(excel_row, column_indices['PAN of the Employee (315)'], csv_row['PAN No.'])
            ws.write(excel_row, column_indices['Name of the Employee (316)'], csv_row['Employee Name'])
            ws.write(excel_row, column_indices['Section Code (317)'], '192A')
            ws.write(excel_row, column_indices['Payment/Credit Date (dd/mm/yyyy) (318)'], 
                    get_last_day_of_month(csv_row['Month']))
            ws.write(excel_row, column_indices['Amount Paid/Credited (320)'], float(csv_row['Gross']))
            ws.write(excel_row, column_indices['TDS (321)'], float(csv_row['Amount Deducted']))
            ws.write(excel_row, column_indices['Surcharge'], 0)  # Separate Surcharge column
            ws.write(excel_row, column_indices['Education Cess (322)'], 0)  # Separate Education Cess column
            ws.write(excel_row, column_indices['Total Tax Deducted (323)'], float(csv_row['Amount Deducted']))
            ws.write(excel_row, column_indices['Total Tax Deposited (324)'], float(csv_row['Amount Deducted']))
            ws.write(excel_row, column_indices['Reason for Non-deduction/Lower Deduction (326)'], '')
            ws.write(excel_row, column_indices['Certificate number for Lower/non deduction (327)'], '')
        
        # Save the modified workbook
        wb.save(excel_file_path)
        
        print(f"Successfully appended {len(csv_df)} rows to '{excel_file_path}'")
        return True
        
    except Exception as e:
        print(f"Error processing files: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to restore backup if error occurred
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, excel_file_path)
                print("Restored original file from backup due to error")
            except:
                pass
                
        return False

if __name__ == "__main__":
    print("CSV to Excel Transfer Tool (Excel 97-2000 Format)")
    print("=" * 50)
    print(f"CSV File: {csv_file_path}")
    print(f"Excel File: {excel_file_path}")
    print("=" * 50)
    
    success = transfer_csv_to_excel()
    
    if success:
        print("\nProcess completed successfully.")
        print(f"Data has been appended to the Employee Details sheet in '{excel_file_path}'")
    else:
        print("\nProcess failed or was cancelled.")