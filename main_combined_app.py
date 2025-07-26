import tkinter as tk
from tkinter import ttk, filedialog
from bin_view import BinViewFrame
from tds_transfer_tool import TDSTransferFrame

def main():
    root = tk.Tk()
    root.title('Combined BIN View & TDS Transfer Tool')
    root.geometry('900x900')
    
    # Shared Excel file selection at the top
    shared_frame = ttk.LabelFrame(root, text="Shared Excel File")
    shared_frame.pack(padx=10, pady=5, fill="x")
    
    excel_frame = ttk.Frame(shared_frame)
    excel_frame.pack(padx=5, pady=5, fill="x")
    
    ttk.Label(excel_frame, text="Excel File:").pack(side="left")
    excel_entry = ttk.Entry(excel_frame, width=70)
    excel_entry.pack(side="left", padx=5, fill="x", expand=True)
    
    def browse_excel():
        filename = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xls")])
        if filename:
            excel_entry.delete(0, tk.END)
            excel_entry.insert(0, filename)
    
    ttk.Button(excel_frame, text="Browse", command=browse_excel).pack(side="left")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=5)
    
    bin_view_tab = BinViewFrame(notebook, excel_entry)
    tds_transfer_tab = TDSTransferFrame(notebook, excel_entry)
    
    notebook.add(bin_view_tab, text='BIN View')
    notebook.add(tds_transfer_tab, text='TDS Transfer Tool')
    
    root.mainloop()

if __name__ == '__main__':
    main() 