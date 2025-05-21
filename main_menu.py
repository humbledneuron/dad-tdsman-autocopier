import tkinter as tk
from tkinter import ttk
import subprocess
import sys


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("TDS Management Tools")
        self.root.geometry("400x400")
        
        # Configure style
        style = ttk.Style()
        style.configure("Custom.TButton", padding=10, font=('Helvetica', 12))
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="TDS Management Tools",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Select a tool to launch:",
            font=('Helvetica', 10)
        )
        desc_label.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # BIN View Tool button
        bin_button = ttk.Button(
            button_frame,
            text="BIN View Tool",
            style="Custom.TButton",
            command=self.launch_bin_tool
        )
        bin_button.pack(pady=10, fill=tk.X)
        
        # TDS Transfer Tool button
        tds_button = ttk.Button(
            button_frame,
            text="TDS Transfer Tool",
            style="Custom.TButton",
            command=self.launch_tds_tool
        )
        tds_button.pack(pady=10, fill=tk.X)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready",
            font=('Helvetica', 9)
        )
        self.status_label.pack(pady=10)
        
    def launch_tds_tool(self):
        try:
            self.status_label.config(text="Launching TDS Transfer Tool...")
            self.root.update()
            
            # Launch the TDS transfer tool in a new process
            subprocess.Popen([sys.executable, "tds_transfer_tool.py"])
            
            self.status_label.config(
                text="TDS Transfer Tool launched successfully"
            )
        except Exception as e:
            self.status_label.config(
                text=f"Error launching TDS Transfer Tool: {str(e)}"
            )
    
    def launch_bin_tool(self):
        try:
            self.status_label.config(text="Launching BIN View Tool...")
            self.root.update()
            
            # Launch the BIN view tool in a new process
            subprocess.Popen([sys.executable, "bin_view.py"])
            
            self.status_label.config(
                text="BIN View Tool launched successfully"
            )
        except Exception as e:
            self.status_label.config(
                text=f"Error launching BIN View Tool: {str(e)}"
            )


def main():
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main() 