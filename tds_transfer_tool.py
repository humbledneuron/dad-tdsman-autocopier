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
month_amount_map = {}

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
    if log_widget:
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_widget.insert(tk.END, f"[TDS Transfer] [{timestamp}] {message}\n")
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
            'Date on Tax Deposited (dd/mm/yyyy) (311)': ['Date on Tax Deposited (dd/mm/yyyy) (311)', 'Date on Tax Deposited', 'Date'],
            'Surcharge': ['Surcharge', 'Surcharge ()', 'surcharge'],
            'Education Cess (303)': ['Education Cess (303)', 'Education Cess', 'Cess'],
            'Interest (304)': ['Interest (304)', 'Interest', 'Interest Amount'],
            'Fee (305)': ['Fee (305)', 'Fee', 'Fee Amount'],
            'Others (306)': ['Others (306)', 'Others', 'Other Amount'],
            'Whether TDS Deposited by Book Entry (308)': ['Whether TDS Deposited by Book Entry (308)', 'Book Entry', 'Book Entry (308)'],
            'TDS (302)': ['TDS (302)', 'TDS', 'Tax Deducted at Source'],
            'Total Tax Deposited (307)': ['Total Tax Deposited (307)', 'Total Tax Deposited', 'Total Tax']
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
            
            amt = row['Amount'] if 'Amount' in row else ''

            row_idx = start_row + idx
            
            ws_challan.write(row_idx, column_indices['BSR Code / 24G Receipt No (309)'], receipt_num, style_regular)
            ws_challan.write(row_idx, column_indices['Surcharge'], 1, style_regular)
            ws_challan.write(row_idx, column_indices['Education Cess (303)'], 0, style_regular)
            ws_challan.write(row_idx, column_indices['Interest (304)'], 0, style_regular)
            ws_challan.write(row_idx, column_indices['Fee (305)'], 0, style_regular)
            ws_challan.write(row_idx, column_indices['Others (306)'], 0, style_regular)
            ws_challan.write(row_idx, column_indices['Whether TDS Deposited by Book Entry (308)'], 'Y', style_regular)
            # Format DDO Serial No as text with leading apostrophe
            ws_challan.write(row_idx, column_indices['Transfer Voucher/Challan Serial No (310)'], ddo_serial, style_text)
            ws_challan.write(row_idx, column_indices['TDS (302)'], amt, style_regular)
            ws_challan.write(row_idx, column_indices['Total Tax Deposited (307)'], amt, style_regular)
            
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

def transfer_to_excel(csv_files, challan_csv, excel_file, log_widget, month_amount_map):
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

                # Clean empty rows
                csv_df = csv_df.dropna(how='all')

                if not csv_df.empty:
                    # Get last row (summary row)
                    last_row = csv_df.iloc[-1]
                    last_value = last_row.iloc[-1]

                    # Extract month from data (IMPORTANT)
                    # Assuming 'Month' column exists
                    if 'Month' in csv_df.columns:
                        month_name = str(csv_df.iloc[0]['Month']).strip()
                    else:
                        # fallback: try from filename
                        month_name = os.path.basename(csv_file).split('.')[0]

                    try:
                        month_amount_map[month_name] = float(last_value)
                    except:
                        month_amount_map[month_name] = 0
                    
                    log_message(log_widget, f"Mapped → {month_name} : {last_value}")

                    # Remove summary row for normal processing
                    csv_df = csv_df.iloc[:-1]
                    
                log_message(log_widget, f"Processing file {file_idx+1}: {os.path.basename(csv_file)} ({len(csv_df)} rows)")
                log_message(log_widget, f"Stored month mapping: {month_amount_map}")

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

class TDSTransferFrame(ttk.Frame):
    def __init__(self, parent, shared_excel_entry, shared_log_text=None):
        super().__init__(parent)
        self.shared_excel_entry = shared_excel_entry
        self.shared_log_text = shared_log_text
        self._build_ui()

    def _build_ui(self):
        file_frame = ttk.LabelFrame(self, text="File Selection")
        file_frame.pack(padx=10, pady=10, fill="x")

        self.csv_files = [None, None, None]
        self.csv_entries = []

        for i in range(3):
            csv_frame = ttk.Frame(file_frame)
            csv_frame.pack(padx=5, pady=5, fill="x")

            ttk.Label(csv_frame, text=f"Employee CSV File {i+1}:").pack(side="left")
            csv_entry = ttk.Entry(csv_frame, width=50)
            csv_entry.pack(side="left", padx=5)
            self.csv_entries.append(csv_entry)

            def browse_csv(idx=i):
                filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
                if filename:
                    self.csv_entries[idx].delete(0, tk.END)
                    self.csv_entries[idx].insert(0, filename)
                    self.csv_files[idx] = filename

            ttk.Button(csv_frame, text="Browse", command=browse_csv).pack(side="left")

        # Remove Challan Details CSV selection

                # log_frame = ttk.LabelFrame(self, text="Log")
        # log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # self.log_text = tk.Text(log_frame, wrap="word", height=15)
        # self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        # scrollbar.pack(side="right", fill="y")
        # self.log_text.config(yscrollcommand=scrollbar.set)

        def process_files():
            for i in range(3):
                self.csv_files[i] = self.csv_entries[i].get()

            excel_file = self.shared_excel_entry.get()

            valid_csv_files = [f for f in self.csv_files if f and os.path.exists(f)]

            if not valid_csv_files:
                messagebox.showerror("Error", "Please select at least one valid Employee Details CSV file")
                return

            if not excel_file or not os.path.exists(excel_file):
                messagebox.showerror("Error", "Please select a valid Excel file")
                return

            # Log to shared log if available
            if self.shared_log_text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.shared_log_text.insert(tk.END, f"[TDS Transfer] [{timestamp}] Starting data transfer process...\n")
                self.shared_log_text.see(tk.END)
            
            # Only pass employee CSVs, not challan_csv
            success = transfer_to_excel(self.csv_files, None, excel_file, self.shared_log_text, self.month_amount_map)
            
            if success:
                if self.shared_log_text:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.shared_log_text.insert(tk.END, f"[TDS Transfer] [{timestamp}] Process completed successfully!\n")
                    self.shared_log_text.see(tk.END)
                messagebox.showinfo("Success", "Data transfer complete")
            else:
                if self.shared_log_text:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.shared_log_text.insert(tk.END, f"[TDS Transfer] [{timestamp}] Process failed!\n")
                    self.shared_log_text.see(tk.END)
                messagebox.showerror("Error", "Transfer failed. See log for details.")

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        process_button = ttk.Button(button_frame, text="Process Files", command=process_files)
        process_button.pack(padx=5, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("TDS Data Transfer Tool")
    root.geometry("700x600")
    
    # Create an instance of the frame and pack it
    transfer_frame = TDSTransferFrame(root)
    transfer_frame.pack(padx=10, pady=10, fill="both", expand=True)
    
    root.mainloop()