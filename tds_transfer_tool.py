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

warnings.filterwarnings('ignore', category=UserWarning)

def get_last_day_of_month(month_name, year=2025):
    try:
        month_number = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }[month_name]
        
        last_day = calendar.monthrange(year, month_number)[1]
        return datetime(year, month_number, last_day)
    except KeyError:
        return datetime(2025, 3, 31)

def parse_date(date_str):
    try:
        if isinstance(date_str, str):
            parts = date_str.split('/')
            if len(parts) == 3:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                return datetime(year, month, day)
        return date_str
    except Exception:
        return date_str

def install_required_libraries():
    try:
        import xlwt
        import xlutils
    except ImportError:
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "xlwt", "xlutils"])

def log_message(log_widget, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    log_widget.see(tk.END)

def process_challan_details(challan_csv, excel_file, rb, wb, log_widget):
    if not challan_csv or not os.path.exists(challan_csv):
        log_message(log_widget, "No challan details CSV file provided, skipping")
        return True
    
    try:
        challan_sheet_index = None
        for idx, sheet_name in enumerate(rb.sheet_names()):
            if sheet_name == 'Challan Details':
                challan_sheet_index = idx
                break
                
        if challan_sheet_index is None:
            log_message(log_widget, "Error: Challan Details sheet not found")
            return False
            
        challan_sheet = rb.sheet_by_index(challan_sheet_index)
        log_message(log_widget, f"Found Challan Details sheet with {challan_sheet.nrows} rows")
        
        header_row = [challan_sheet.cell_value(0, col) for col in range(challan_sheet.ncols)]
        
        ws_challan = wb.get_sheet(challan_sheet_index)
        
        column_mappings = {
            'BSR Code / 24G Receipt No (309)': ['BSR Code / 24G Receipt No (309)', 'BSR Code', '24G Receipt No', 'Receipt No'],
            'Transfer Voucher/Challan Serial No (310)': ['Transfer Voucher/Challan Serial No (310)', 'Challan Serial No', 'DDO Serial No'],
            'Date on Tax Deposited (dd/mm/yyyy) (311)': ['Date on Tax Deposited (dd/mm/yyyy) (311)', 'Date on Tax Deposited', 'Date']
        }
        
        column_indices = {}
        for col_key, possible_names in column_mappings.items():
            column_indices[col_key] = None
            for possible_name in possible_names:
                for col_idx, header in enumerate(header_row):
                    if possible_name.lower() in header.lower():
                        column_indices[col_key] = col_idx
                        break
                if column_indices[col_key] is not None:
                    break
        
        missing_columns = [col for col, idx in column_indices.items() if idx is None]
        if missing_columns:
            log_message(log_widget, f"Warning: Columns not found in Challan Details sheet: {missing_columns}")
            return False
        
        # Explicitly tell pandas to keep leading zeros by setting dtypes
        challan_df = pd.read_csv(challan_csv, dtype={
            'DDO Serial No.': str,  # Force string type to preserve leading zeros
            'Receipt Number': str    # Also treat Receipt Number as string
        })
        log_message(log_widget, f"Read challan details CSV with {len(challan_df)} rows")
        
        if challan_df.empty:
            log_message(log_widget, "Challan details CSV is empty, skipping")
            return True
            
        font = xlwt.Font()
        font.name = 'Calibri'
        font.height = 220

        style_regular = xlwt.XFStyle()
        style_regular.font = font
        
        # Create text style specifically for the Challan Serial No column
        style_text = xlwt.XFStyle()
        style_text.font = font
        style_text.num_format_str = '@'  # Format as text
        
        style_date = xlwt.XFStyle()
        style_date.font = font
        style_date.num_format_str = 'DD/MM/YYYY'
        
        # Start at row 1 (after header) to overwrite existing data
        start_row = 1
        
        for idx, row in challan_df.iterrows():
            receipt_num = str(row['Receipt Number']) if 'Receipt Number' in row else ''
            
            # Force DDO Serial No to be treated as text with leading zeros
            if 'DDO Serial No.' in row:
                ddo_serial = str(row['DDO Serial No.'])
                # Add a leading apostrophe to force Excel to treat it as text
                if ddo_serial.isdigit():
                    ddo_serial = str(ddo_serial)
            else:
                ddo_serial = ''
                
            date_str = row['Date'] if 'Date' in row else ''
            
            date_obj = parse_date(date_str)
            
            row_idx = start_row + idx
            
            ws_challan.write(row_idx, column_indices['BSR Code / 24G Receipt No (309)'], receipt_num, style_regular)
            # Format DDO Serial No as text with leading apostrophe
            ws_challan.write(row_idx, column_indices['Transfer Voucher/Challan Serial No (310)'], ddo_serial, style_text)
            
            if isinstance(date_obj, datetime):
                ws_challan.write(row_idx, column_indices['Date on Tax Deposited (dd/mm/yyyy) (311)'], date_obj, style_date)
            else:
                ws_challan.write(row_idx, column_indices['Date on Tax Deposited (dd/mm/yyyy) (311)'], date_str, style_regular)
        
        log_message(log_widget, f"Overwrote Challan Details with {len(challan_df)} rows")
        return True
        
    except Exception as e:
        log_message(log_widget, f"Error processing Challan Details: {str(e)}")
        import traceback
        error_details = traceback.format_exc()
        log_message(log_widget, f"Details: {error_details}")
        return False

def transfer_to_excel(csv_files, challan_csv, excel_file, log_widget):
    install_required_libraries()
    
    valid_csv_files = [f for f in csv_files if f and os.path.exists(f)]
    if not valid_csv_files and (not challan_csv or not os.path.exists(challan_csv)):
        log_message(log_widget, "Error: No valid CSV files to process")
        return False
    
    if not excel_file or not os.path.exists(excel_file):
        log_message(log_widget, f"Error: Excel file '{excel_file}' does not exist")
        return False
    
    backup_file = f"{excel_file}.backup"
    try:
        shutil.copy2(excel_file, backup_file)
        log_message(log_widget, f"Created backup at '{backup_file}'")
    except Exception as e:
        log_message(log_widget, f"Warning: Could not create backup: {e}")
    
    try:
        rb = xlrd.open_workbook(excel_file, formatting_info=True)
        wb = copy(rb)
        
        # Process Challan Details first
        if challan_csv and os.path.exists(challan_csv):
            log_message(log_widget, f"Processing Challan Details from: {os.path.basename(challan_csv)}")
            challan_result = process_challan_details(challan_csv, excel_file, rb, wb, log_widget)
            if not challan_result:
                log_message(log_widget, "Failed to process Challan Details")
        
        # Process Employee Details CSV files
        if valid_csv_files:
            employee_sheet_index = None
            for idx, sheet_name in enumerate(rb.sheet_names()):
                if sheet_name == 'Employee Details':
                    employee_sheet_index = idx
                    break
                    
            if employee_sheet_index is None:
                log_message(log_widget, "Error: Employee Details sheet not found")
                return False
                
            employee_sheet = rb.sheet_by_index(employee_sheet_index)
            log_message(log_widget, f"Found Employee Details sheet with {employee_sheet.nrows} rows")
            
            header_row = [employee_sheet.cell_value(0, col) for col in range(employee_sheet.ncols)]
            
            ws = wb.get_sheet(employee_sheet_index)
            
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
            
            column_indices = {}
            for col_key, possible_names in column_mappings.items():
                column_indices[col_key] = None
                for possible_name in possible_names:
                    for col_idx, header in enumerate(header_row):
                        if possible_name.lower() in header.lower():
                            column_indices[col_key] = col_idx
                            break
                    if column_indices[col_key] is not None:
                        break
            
            missing_columns = [col for col, idx in column_indices.items() if idx is None]
            if missing_columns:
                log_message(log_widget, f"Warning: Columns not found in Employee Details: {missing_columns}")
                return False
            
            font = xlwt.Font()
            font.name = 'Calibri'
            font.height = 220

            style_regular = xlwt.XFStyle()
            style_regular.font = font
            
            style_right_aligned = xlwt.XFStyle()
            style_right_aligned.font = font
            style_right_aligned.alignment.horz = xlwt.Alignment.HORZ_RIGHT
            
            style_date = xlwt.XFStyle()
            style_date.font = font
            style_date.num_format_str = 'DD/MM/YYYY'
            
            start_row = employee_sheet.nrows
            current_row = start_row
            total_processed = 0
            
            for file_idx, csv_file in enumerate(valid_csv_files):
                if not csv_file:
                    continue
                    
                challan_index = str(file_idx + 1)
                
                csv_df = pd.read_csv(csv_file)
                
                if not csv_df.empty:
                    csv_df = csv_df.iloc[:-1]
                    
                log_message(log_widget, f"Processing file {file_idx+1}: {os.path.basename(csv_file)} ({len(csv_df)} rows)")
                
                if csv_df.empty:
                    continue
                    
                for _, csv_row in csv_df.iterrows():
                    payment_date = get_last_day_of_month(csv_row['Month'])
                    
                    ws.write(current_row, column_indices['Employee Serial No (313)'], float(csv_row['Sno.']), style_regular)
                    ws.write(current_row, column_indices['Challan Serial Reference (301)'], challan_index, style_right_aligned)
                    ws.write(current_row, column_indices['PAN of the Employee (315)'], csv_row['PAN No.'], style_regular)
                    ws.write(current_row, column_indices['Name of the Employee (316)'], csv_row['Employee Name'], style_regular)
                    ws.write(current_row, column_indices['Section Code (317)'], '192A', style_regular)
                    ws.write(current_row, column_indices['Payment/Credit Date (dd/mm/yyyy) (318)'], payment_date, style_date)
                    ws.write(current_row, column_indices['Amount Paid/Credited (320)'], float(csv_row['Gross']), style_regular)
                    ws.write(current_row, column_indices['TDS (321)'], float(csv_row['Amount Deducted']), style_regular)
                    ws.write(current_row, column_indices['Surcharge'], 0, style_regular)
                    ws.write(current_row, column_indices['Education Cess (322)'], 0, style_regular)
                    ws.write(current_row, column_indices['Total Tax Deducted (323)'], float(csv_row['Amount Deducted']), style_regular)
                    ws.write(current_row, column_indices['Total Tax Deposited (324)'], float(csv_row['Amount Deducted']), style_regular)
                    ws.write(current_row, column_indices['Reason for Non-deduction/Lower Deduction (326)'], '', style_regular)
                    ws.write(current_row, column_indices['Certificate number for Lower/non deduction (327)'], '', style_regular)
                    
                    current_row += 1
                
                total_processed += len(csv_df)
        
        wb.save(excel_file)
        
        log_message(log_widget, f"Successfully processed data to '{excel_file}'")
        return True
        
    except Exception as e:
        log_message(log_widget, f"Error: {str(e)}")
        import traceback
        error_details = traceback.format_exc()
        log_message(log_widget, f"Details: {error_details}")
        
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, excel_file)
                log_message(log_widget, "Restored file from backup")
            except:
                pass
                
        return False

def create_gui():
    root = tk.Tk()
    root.title("TDS Data Transfer Tool")
    root.geometry("700x600")
    
    file_frame = ttk.LabelFrame(root, text="File Selection")
    file_frame.pack(padx=10, pady=10, fill="x")
    
    csv_files = [None, None, None]
    csv_entries = []
    
    for i in range(3):
        csv_frame = ttk.Frame(file_frame)
        csv_frame.pack(padx=5, pady=5, fill="x")
        
        ttk.Label(csv_frame, text=f"Employee CSV File {i+1}:").pack(side="left")
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
    
    # Add Challan Details CSV selection
    challan_frame = ttk.Frame(file_frame)
    challan_frame.pack(padx=5, pady=5, fill="x")
    
    ttk.Label(challan_frame, text="Challan Details CSV:").pack(side="left")
    challan_entry = ttk.Entry(challan_frame, width=50)
    challan_entry.pack(side="left", padx=5)
    
    challan_csv = [None]
    
    def browse_challan():
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            challan_entry.delete(0, tk.END)
            challan_entry.insert(0, filename)
            challan_csv[0] = filename
    
    ttk.Button(challan_frame, text="Browse", command=browse_challan).pack(side="left")
    
    # XLS file selection
    xls_frame = ttk.Frame(file_frame)
    xls_frame.pack(padx=5, pady=5, fill="x")
    
    ttk.Label(xls_frame, text="Excel File:").pack(side="left")
    xls_entry = ttk.Entry(xls_frame, width=50)
    xls_entry.pack(side="left", padx=5)
    
    excel_file = [None]
    
    def browse_xls():
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xls")])
        if filename:
            xls_entry.delete(0, tk.END)
            xls_entry.insert(0, filename)
            excel_file[0] = filename
    
    ttk.Button(xls_frame, text="Browse", command=browse_xls).pack(side="left")
    
    log_frame = ttk.LabelFrame(root, text="Log")
    log_frame.pack(padx=10, pady=10, fill="both", expand=True)
    
    log_text = tk.Text(log_frame, wrap="word", height=15)
    log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    scrollbar = ttk.Scrollbar(log_text, command=log_text.yview)
    scrollbar.pack(side="right", fill="y")
    log_text.config(yscrollcommand=scrollbar.set)
    
    def process_files():
        for i in range(3):
            csv_files[i] = csv_entries[i].get()
        
        challan_csv[0] = challan_entry.get()
        excel_file[0] = xls_entry.get()
        
        valid_csv_files = [f for f in csv_files if f and os.path.exists(f)]
        
        if not valid_csv_files and (not challan_csv[0] or not os.path.exists(challan_csv[0])):
            messagebox.showerror("Error", "Please select at least one valid CSV file")
            return
        
        if not excel_file[0] or not os.path.exists(excel_file[0]):
            messagebox.showerror("Error", "Please select a valid Excel file")
            return
        
        log_text.delete(1.0, tk.END)
        
        log_message(log_text, "Starting data transfer process...")
        
        success = transfer_to_excel(csv_files, challan_csv[0], excel_file[0], log_text)
        
        if success:
            log_message(log_text, "Process completed successfully!")
            messagebox.showinfo("Success", "Data transfer complete")
        else:
            log_message(log_text, "Process failed!")
            messagebox.showerror("Error", "Transfer failed. See log for details.")
    
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    process_button = ttk.Button(button_frame, text="Process Files", command=process_files)
    process_button.pack(padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()