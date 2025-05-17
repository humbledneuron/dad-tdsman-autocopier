import pandas as pd
import os
import shutil
import warnings
import calendar
import xlrd
import xlwt
from xlutils.copy import copy
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)

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

def log_message(log_widget, message):
    """Add a message to the log widget with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    log_widget.see(tk.END)  # Scroll to the end

def transfer_to_excel(csv_files, excel_file, log_widget):
    """
    Transfer data from CSV files to the Excel file
    """
    # Install required libraries
    install_required_libraries()
    
    valid_csv_files = [f for f in csv_files if f and os.path.exists(f)]
    if not valid_csv_files:
        log_message(log_widget, "Error: No valid CSV files to process")
        return False
    
    if not excel_file or not os.path.exists(excel_file):
        log_message(log_widget, f"Error: Excel file '{excel_file}' does not exist")
        return False
    
    # Create a backup of the original Excel file
    backup_file = f"{excel_file}.backup"
    try:
        shutil.copy2(excel_file, backup_file)
        log_message(log_widget, f"Created backup at '{backup_file}'")
    except Exception as e:
        log_message(log_widget, f"Warning: Could not create backup: {e}")
    
    try:
        # Open the .xls file with xlrd
        rb = xlrd.open_workbook(excel_file, formatting_info=True)
        
        # Find the Employee Details sheet index
        employee_sheet_index = None
        for idx, sheet_name in enumerate(rb.sheet_names()):
            if sheet_name == 'Employee Details':
                employee_sheet_index = idx
                break
                
        if employee_sheet_index is None:
            log_message(log_widget, "Error: Employee Details sheet not found in the Excel file")
            return False
            
        # Read the Employee Details sheet
        employee_sheet = rb.sheet_by_index(employee_sheet_index)
        log_message(log_widget, f"Found Employee Details sheet with {employee_sheet.nrows} rows")
        
        # Get header row (assuming it's the first row)
        header_row = [employee_sheet.cell_value(0, col) for col in range(employee_sheet.ncols)]
        
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
                        log_message(log_widget, f"Found column '{col_key}' at index {col_idx}")
                        break
                if column_indices[col_key] is not None:
                    break
        
        # Check if all needed columns were found
        missing_columns = [col for col, idx in column_indices.items() if idx is None]
        if missing_columns:
            log_message(log_widget, f"Warning: The following columns were not found: {missing_columns}")
            return False
        
        # Start adding rows after the existing data
        start_row = employee_sheet.nrows
        current_row = start_row
        total_processed = 0
        
        # Process each CSV file separately with its own Challan Serial Reference
        for file_idx, csv_file in enumerate(valid_csv_files):
            # The Challan Serial Reference number corresponds to the file number (1-based)
            challan_index = str(file_idx + 1)
            
            # Read the CSV file
            csv_df = pd.read_csv(csv_file)
            
            # Skip the last row
            if not csv_df.empty:
                csv_df = csv_df.iloc[:-1]
                
            log_message(log_widget, f"Processing CSV file {file_idx+1}: {csv_file}")
            log_message(log_widget, f"  - {len(csv_df)} rows (after removing last row)")
            log_message(log_widget, f"  - Using Challan Serial Reference: {challan_index}")
            
            if csv_df.empty:
                log_message(log_widget, f"  - Skipping file (no data)")
                continue
                
            # Add data from this CSV file
            for _, csv_row in csv_df.iterrows():
                # Write data to appropriate columns
                ws.write(current_row, column_indices['Employee Serial No (313)'], float(csv_row['Sno.']))
                # Use the file index as Challan Serial Reference
                ws.write(current_row, column_indices['Challan Serial Reference (301)'], challan_index)
                ws.write(current_row, column_indices['PAN of the Employee (315)'], csv_row['PAN No.'])
                ws.write(current_row, column_indices['Name of the Employee (316)'], csv_row['Employee Name'])
                ws.write(current_row, column_indices['Section Code (317)'], '192A')
                ws.write(current_row, column_indices['Payment/Credit Date (dd/mm/yyyy) (318)'], 
                        get_last_day_of_month(csv_row['Month']))
                ws.write(current_row, column_indices['Amount Paid/Credited (320)'], float(csv_row['Gross']))
                ws.write(current_row, column_indices['TDS (321)'], float(csv_row['Amount Deducted']))
                ws.write(current_row, column_indices['Surcharge'], 0)  # Separate Surcharge column
                ws.write(current_row, column_indices['Education Cess (322)'], 0)  # Separate Education Cess column
                ws.write(current_row, column_indices['Total Tax Deducted (323)'], float(csv_row['Amount Deducted']))
                ws.write(current_row, column_indices['Total Tax Deposited (324)'], float(csv_row['Amount Deducted']))
                ws.write(current_row, column_indices['Reason for Non-deduction/Lower Deduction (326)'], '')
                ws.write(current_row, column_indices['Certificate number for Lower/non deduction (327)'], '')
                
                current_row += 1
            
            total_processed += len(csv_df)
            log_message(log_widget, f"  - Added {len(csv_df)} rows")
        
        # Save the modified workbook
        wb.save(excel_file)
        
        log_message(log_widget, f"Successfully appended {total_processed} rows to '{excel_file}'")
        return True
        
    except Exception as e:
        log_message(log_widget, f"Error processing files: {e}")
        import traceback
        error_details = traceback.format_exc()
        log_message(log_widget, f"Error details: {error_details}")
        
        # Try to restore backup if error occurred
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, excel_file)
                log_message(log_widget, "Restored original file from backup due to error")
            except:
                pass
                
        return False

def create_gui():
    """Create the GUI for the application"""
    # Create the main window
    root = tk.Tk()
    root.title("TDS Data Transfer Tool")
    root.geometry("700x600")
    
    # Create a frame for the file selection
    file_frame = ttk.LabelFrame(root, text="File Selection")
    file_frame.pack(padx=10, pady=10, fill="x")
    
    # CSV file selection
    csv_files = [None, None, None]
    csv_entries = []
    
    # Info label for Challan Serial Reference
    info_label = ttk.Label(file_frame, 
                          text="Note: Challan Serial Reference will be 1 for CSV File 1, 2 for CSV File 2, and 3 for CSV File 3",
                          wraplength=650)
    info_label.pack(padx=5, pady=5, fill="x")
    
    for i in range(3):
        csv_frame = ttk.Frame(file_frame)
        csv_frame.pack(padx=5, pady=5, fill="x")
        
        ttk.Label(csv_frame, text=f"CSV File {i+1} (Challan Index {i+1}):").pack(side="left")
        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side="left", padx=5)
        csv_entries.append(csv_entry)
        
        def browse_csv(idx=i):
            filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if filename:
                csv_entries[idx].delete(0, tk.END)
                csv_entries[idx].insert(0, filename)
                csv_files[idx] = filename
        
        ttk.Button(csv_frame, text="Browse", command=browse_csv).pack(side="left")
    
    # XLS file selection
    xls_frame = ttk.Frame(file_frame)
    xls_frame.pack(padx=5, pady=5, fill="x")
    
    ttk.Label(xls_frame, text="Excel File:").pack(side="left")
    xls_entry = ttk.Entry(xls_frame, width=50)
    xls_entry.pack(side="left", padx=5)
    
    excel_file = [None]  # Using a list to allow modification in nested function
    
    def browse_xls():
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xls")])
        if filename:
            xls_entry.delete(0, tk.END)
            xls_entry.insert(0, filename)
            excel_file[0] = filename
    
    ttk.Button(xls_frame, text="Browse", command=browse_xls).pack(side="left")
    
    # Log area
    log_frame = ttk.LabelFrame(root, text="Log")
    log_frame.pack(padx=10, pady=10, fill="both", expand=True)
    
    log_text = tk.Text(log_frame, wrap="word", height=15)
    log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Add a scrollbar to the log
    scrollbar = ttk.Scrollbar(log_text, command=log_text.yview)
    scrollbar.pack(side="right", fill="y")
    log_text.config(yscrollcommand=scrollbar.set)
    
    # Process button
    def process_files():
        # Get file paths from entries
        for i in range(3):
            csv_files[i] = csv_entries[i].get()
        
        excel_file[0] = xls_entry.get()
        
        # Validate inputs
        valid_csv_files = [f for f in csv_files if f and os.path.exists(f)]
        
        if not valid_csv_files:
            messagebox.showerror("Error", "Please select at least one valid CSV file")
            return
        
        if not excel_file[0] or not os.path.exists(excel_file[0]):
            messagebox.showerror("Error", "Please select a valid Excel file")
            return
        
        # Clear the log
        log_text.delete(1.0, tk.END)
        
        # Process the files
        log_message(log_text, "Starting data transfer process...")
        for i, f in enumerate(csv_files):
            if f:
                log_message(log_text, f"CSV File {i+1} (Challan Index {i+1}): {f}")
            else:
                log_message(log_text, f"CSV File {i+1}: Not selected")
        log_message(log_text, f"Excel File: {excel_file[0]}")
        
        success = transfer_to_excel(csv_files, excel_file[0], log_text)
        
        if success:
            log_message(log_text, "Process completed successfully!")
            messagebox.showinfo("Success", "Data has been successfully transferred to the Excel file")
        else:
            log_message(log_text, "Process failed!")
            messagebox.showerror("Error", "Failed to transfer data. See the log for details.")
    
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    process_button = ttk.Button(button_frame, text="Process Files", command=process_files)
    process_button.pack(padx=5, pady=5)
    
    # Run the GUI
    root.mainloop()

if __name__ == "__main__":
    # Start the GUI
    create_gui()