import tkinter as tk
from tkinter import ttk
from bin_view import BinViewFrame
from tds_transfer_tool import TDSTransferFrame

def main():
    root = tk.Tk()
    root.title('Combined BIN View & TDS Transfer Tool')
    root.geometry('900x900')
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    bin_view_tab = BinViewFrame(notebook)
    tds_transfer_tab = TDSTransferFrame(notebook)
    notebook.add(bin_view_tab, text='BIN View')
    notebook.add(tds_transfer_tab, text='TDS Transfer Tool')
    root.mainloop()

if __name__ == '__main__':
    main() 