import pandas as pd
import os, shutil, warnings, calendar, xlrd, xlwt
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

def install_required_libraries():
    try:
        import xlwt, xlutils
    except ImportError:
        import sys, subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "xlwt", "xlutils"])

def log_message(log_widget, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    log_widget.see(tk.END)

def transfer_to_excel(csv_files, excel_file, log_widget):
    install_required_libraries()
    
    valid_csv_files = [f for f in csv_files if f and os.path.exists(f)]
    if not valid_csv_files:
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
        
        wb = copy(rb)
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
            log_message(log_widget, f"Warning: Columns not found: {missing_columns}")
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
        
        log_message(log_widget, f"Successfully processed {total_processed} rows")
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
    root.geometry("700x550")
    
    file_frame = ttk.LabelFrame(root, text="File Selection")
    file_frame.pack(padx=10, pady=10, fill="x")
    
    csv_files = [None, None, None]
    csv_entries = []
    
    for i in range(3):
        csv_frame = ttk.Frame(file_frame)
        csv_frame.pack(padx=5, pady=5, fill="x")
        
        ttk.Label(csv_frame, text=f"CSV File {i+1}:").pack(side="left")
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
        
        excel_file[0] = xls_entry.get()
        
        valid_csv_files = [f for f in csv_files if f and os.path.exists(f)]
        
        if not valid_csv_files:
            messagebox.showerror("Error", "Please select at least one valid CSV file")
            return
        
        if not excel_file[0] or not os.path.exists(excel_file[0]):
            messagebox.showerror("Error", "Please select a valid Excel file")
            return
        
        log_text.delete(1.0, tk.END)
        
        log_message(log_text, "Starting data transfer process...")
        
        success = transfer_to_excel(csv_files, excel_file[0], log_text)
        
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