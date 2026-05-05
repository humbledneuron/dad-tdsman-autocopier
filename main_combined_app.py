import tkinter as tk
from tkinter import ttk, filedialog, Text, Scrollbar
from bin_view import BinViewFrame
from tds_transfer_tool import TDSTransferFrame

def main():
    month_amount_map = {}

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

    style = ttk.Style()
    style.theme_use('default')  # or 'clam' for better control

    style.configure("TNotebook.Tab",
        background="#d9d9d9",
        foreground="black",
        padding=[10, 5]
    )

    style.map("TNotebook.Tab",
        background=[("selected", "#4CAF50")],  # green when active
        foreground=[("selected", "white")]
    )

    # Create the notebook and all tabs first
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=5)

    bin_view_tab = BinViewFrame(notebook, excel_entry, None)
    tds_transfer_tab = TDSTransferFrame(notebook, excel_entry, None)

    # Inject shared data storage
    bin_view_tab.month_amount_map = month_amount_map
    tds_transfer_tab.month_amount_map = month_amount_map

    notebook.add(tds_transfer_tab, text='TDS Transfer Tool')
    notebook.add(bin_view_tab, text='BIN View')


    # Create Logs tab and log display frame
    logs_frame = ttk.Frame(notebook)
    log_display_frame = ttk.LabelFrame(logs_frame, text="Combined Application Logs")
    log_display_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Now create the shared log text widget with the correct parent
    shared_log_text = Text(log_display_frame, wrap="word", height=20)
    shared_log_scrollbar = Scrollbar(shared_log_text, command=shared_log_text.yview)
    shared_log_scrollbar.pack(side="right", fill="y")
    shared_log_text.config(yscrollcommand=shared_log_scrollbar.set)
    shared_log_text.pack(fill='both', expand=True, padx=5, pady=5)

    # Now set the shared_log_text in both frames
    bin_view_tab.shared_log_text = shared_log_text
    tds_transfer_tab.shared_log_text = shared_log_text

    notebook.add(logs_frame, text='Logs')

    root.mainloop()

if __name__ == '__main__':
    main() 