# flake8: noqa
import time
import csv
import os
from tkinter import *
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

driver = None
amount_entries = []  # To store dynamically created entry fields

def start_browser_and_fill_fields():
    global driver

    tan = tan_entry.get()
    form_type = form_type_var.get()
    ain = ain_entry.get()
    from_month = from_month_var.get()
    from_year = from_year_var.get()
    to_month = to_month_var.get()
    to_year = to_year_var.get()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error initializing ChromeDriver: {e}")
        # Fallback to direct ChromeDriver path
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"Fallback also failed: {e}")
            return

    driver.get("https://onlineservices.tin.egov-nsdl.com/TIN/JSP/etbaf/ViewBIN.jsp")

    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.NAME, "tan"))).send_keys(tan)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "formtype")))).select_by_visible_text(form_type)
    wait.until(EC.presence_of_element_located((By.NAME, "ain"))).send_keys(ain)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "fmonth")))).select_by_visible_text(from_month)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "fyear")))).select_by_visible_text(from_year)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "tmonth")))).select_by_visible_text(to_month)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "tyear")))).select_by_visible_text(to_year)

    print("Browser started and fields filled (excluding CAPTCHA).")

def submit_captcha():
    global driver
    if not driver:
        print("Browser not launched yet.")
        return

    captcha = captcha_entry.get()
    try:
        driver.find_element(By.NAME, "captcha").send_keys(captcha)
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        print("CAPTCHA submitted. Button clicked.")
        
        # Wait for BIN table to load and then create amount fields
        time.sleep(2)
        create_amount_fields()
    except Exception as e:
        print(f"Error submitting CAPTCHA: {e}")

def create_amount_fields():
    """Creates the initial amount fields in the GUI after CAPTCHA is submitted"""
    global driver, amount_entries
    
    try:
        # Clear any previous amount entries
        clear_amount_fields()
        
        # Find all table rows with BIN data
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
        
        if not rows:
            print("No BIN records found to create amount fields.")
            return
            
        # Create a labeled frame for amount entries
        amounts_frame = LabelFrame(main_frame, text="Enter Amounts for Each Record", padx=10, pady=10)
        amounts_frame.pack(fill=X, pady=10)
        
        # Create header
        header_frame = Frame(amounts_frame)
        header_frame.pack(fill=X)
        Label(header_frame, text="Receipt No.", width=15).grid(row=0, column=0)
        Label(header_frame, text="Date", width=15).grid(row=0, column=1)
        Label(header_frame, text="Verification", width=15).grid(row=0, column=2)
        Label(header_frame, text="Amount", width=15).grid(row=0, column=3)
        ttk.Separator(amounts_frame, orient='horizontal').pack(fill=X, pady=5)
        
        # Create amount entry for each BIN record
        for i, row in enumerate(rows):
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 9:
                receipt_number = cols[3].text.strip()
                date = cols[5].text.strip()
                verification_alert = cols[9].text.strip() if len(cols) > 9 else "Not Verified"
                
                # Create a frame for this entry
                entry_frame = Frame(amounts_frame)
                entry_frame.pack(fill=X, pady=2)
                
                # Add labels and entry field
                Label(entry_frame, text=receipt_number, width=15).grid(row=0, column=0)
                Label(entry_frame, text=date, width=15).grid(row=0, column=1)
                
                # Add verification alert label
                verification_label = Label(entry_frame, text=verification_alert, width=15)
                if verification_alert == "Amount Matches":
                    verification_label.configure(fg="green")
                elif verification_alert == "Mismatch in Amount":
                    verification_label.configure(fg="red")
                else:
                    verification_label.configure(fg="black")
                verification_label.grid(row=0, column=2)
                
                # Create amount entry field
                amount_entry = Entry(entry_frame, width=15)
                amount_entry.grid(row=0, column=3)
                amount_entry.insert(0, "")  # Start with empty field for manual entry
                
                # Store the entry field along with its index and verification label for later reference
                amount_entries.append((i, amount_entry, verification_label))
        
        # Add buttons for applying amounts and verifying
        button_frame = Frame(amounts_frame)
        button_frame.pack(fill=X, pady=10)
        
        Button(button_frame, text="Apply Amounts & Check All Boxes", 
               command=apply_amounts_and_check_boxes,
               bg="#4CAF50", fg="white").pack(side=LEFT, padx=5, fill=X, expand=True)
        
        Button(button_frame, text="Verify Amounts", 
               command=verify_amounts,
               bg="#2196F3", fg="white").pack(side=LEFT, padx=5, fill=X, expand=True)
        
        Button(button_frame, text="Update Matching Amounts", 
               command=update_matching_amounts,
               bg="#FF9800", fg="white").pack(side=LEFT, padx=5, fill=X, expand=True)
        
        print(f"Created {len(amount_entries)} amount entry fields for BIN records.")
        
    except Exception as e:
        print(f"Error creating amount fields: {e}")

def clear_amount_fields():
    """Clears all existing amount fields from the GUI"""
    global amount_entries
    
    # Clear the list of entry fields
    amount_entries = []
    
    # Remove any existing amount frames
    for widget in main_frame.winfo_children():
        if isinstance(widget, LabelFrame) and widget.cget("text") == "Enter Amounts for Each Record":
            widget.destroy()

def apply_amounts_and_check_boxes():
    """Applies the manually entered amounts to the browser form and checks all boxes"""
    global driver, amount_entries
    
    if not driver:
        print("Browser not launched yet.")
        return
    
    try:
        # Get all amount fields in the browser
        browser_amount_fields = driver.find_elements(By.XPATH, "//input[contains(@name, 'amt')]")
        
        # Get all checkboxes
        checkboxes = driver.find_elements(By.XPATH, "//input[contains(@name, 'chk')]")
        
        # Apply amounts from GUI to browser
        amounts_applied = 0
        for idx, entry_field, _ in amount_entries:
            if idx < len(browser_amount_fields):
                amount = entry_field.get()
                if amount:  # Only apply if amount is not empty
                    browser_amount_fields[idx].clear()
                    browser_amount_fields[idx].send_keys(amount)
                    amounts_applied += 1
        
        # Check all boxes
        boxes_checked = 0
        for checkbox in checkboxes:
            if not checkbox.is_selected():
                checkbox.click()
                boxes_checked += 1
        
        print(f"✅ Applied {amounts_applied} amounts from GUI to browser and checked {boxes_checked} boxes.")
    
    except Exception as e:
        print(f"Error applying amounts and checking boxes: {e}")

def verify_amounts():
    """Clicks the 'Verify Amount' button and updates verification status"""
    global driver
    
    if not driver:
        print("Browser not launched yet.")
        return
    
    try:
        # Click the Verify Amount button
        verify_button = driver.find_element(By.XPATH, "//input[@value='Verify Amount']")
        verify_button.click()
        print("Clicked 'Verify Amount' button. Waiting for verification...")
        
        # Wait for page to reload with verification results
        time.sleep(2)
        
        # Update verification status in the GUI
        update_verification_status()
        
    except Exception as e:
        print(f"Error verifying amounts: {e}")

def update_verification_status():
    """Updates the verification status labels in the GUI"""
    global driver, amount_entries
    
    try:
        # Find all table rows with BIN data
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
        
        if not rows:
            print("No BIN records found to update verification status.")
            return
        
        matches_found = 0
        mismatches_found = 0
        
        # Update verification status for each row
        for i, row in enumerate(rows):
            if i < len(amount_entries):
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 10:
                    verification_alert = cols[9].text.strip()
                    
                    # Update the verification label in GUI
                    _, _, verification_label = amount_entries[i]
                    verification_label.config(text=verification_alert)
                    
                    if verification_alert == "Amount Matches":
                        verification_label.config(fg="green")
                        matches_found += 1
                    elif verification_alert == "Mismatch in Amount":
                        verification_label.config(fg="red")
                        mismatches_found += 1
        
        print(f"Verification complete: {matches_found} matches, {mismatches_found} mismatches.")
        
    except Exception as e:
        print(f"Error updating verification status: {e}")

def update_matching_amounts():
    """Updates GUI fields with amounts from matched entries"""
    global driver, amount_entries
    
    try:
        # Find all table rows with BIN data
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
        
        if not rows:
            print("No BIN records found to update matching amounts.")
            return
        
        matches_updated = 0
        
        # Update matching amounts for each row
        for i, row in enumerate(rows):
            if i < len(amount_entries):
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 10:
                    verification_alert = cols[9].text.strip()
                    
                    if verification_alert == "Amount Matches":
                        # Get the amount from the browser field
                        try:
                            amount_field = cols[7].find_element(By.TAG_NAME, "input")
                            existing_amount = amount_field.get_attribute("value")
                            
                            if existing_amount:
                                # Update the GUI entry field
                                idx, entry_field, _ = amount_entries[i]
                                entry_field.delete(0, END)
                                entry_field.insert(0, existing_amount)
                                entry_field.config(bg="#e6ffe6")  # Light green background
                                matches_updated += 1
                        except:
                            pass
        
        print(f"✅ Updated {matches_updated} matching amounts in the GUI.")
        
    except Exception as e:
        print(f"Error updating matching amounts: {e}")

def view_bin_data():
    global driver
    if not driver:
        print("Browser not launched yet.")
        return
        
    time.sleep(3)
    extract_bin_data()

def extract_bin_data():
    global driver, amount_entries
    try:
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
        data_list = []

        for i, row in enumerate(rows):
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 9:
                record = {
                    # "AIN": cols[1].text.strip(),
                    "Receipt Number": cols[3].text.strip(),
                    "DDO Serial No.": cols[4].text.strip(),
                    "Date": cols[5].text.strip(),
                }
                
                # Add verification alert if available
                # if len(cols) >= 10:
                #     record["Verification Alert"] = cols[9].text.strip()
                
                # Get amount from GUI entry field if available
                if i < len(amount_entries):
                    _, entry_field, _ = amount_entries[i]
                    amount = entry_field.get()
                    record["Amount"] = amount if amount else ""
                else:
                    record["Amount"] = ""
                
                data_list.append(record)

        if not data_list:
            print("No BIN records found.")
            return

        csv_file = "bin_table_data.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data_list[0].keys())
            writer.writeheader()
            writer.writerows(data_list)

        print(f"\n✅ BIN data saved to CSV: {os.path.abspath(csv_file)}")
            
    except Exception as e:
        print(f"Error extracting table data: {e}")

# GUI setup
root = Tk()
root.title("BIN View Automation")
root.geometry("700x800")  # Increased size to accommodate dynamic fields

# Create main frame with scrollbar for better organization
main_frame_container = Frame(root)
main_frame_container.pack(expand=True, fill=BOTH)

# Add scrollbar
scrollbar = Scrollbar(main_frame_container)
scrollbar.pack(side=RIGHT, fill=Y)

# Create canvas with scrollbar
canvas = Canvas(main_frame_container, yscrollcommand=scrollbar.set)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=canvas.yview)

# Create main frame inside canvas
main_frame = Frame(canvas)
canvas_window = canvas.create_window((0, 0), window=main_frame, anchor='nw')

# Configure canvas to resize with window
def configure_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"), width=event.width)
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind('<Configure>', configure_canvas)
main_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Add padding to main frame
main_frame.configure(padx=20, pady=20)

# TAN Section
tan_frame = Frame(main_frame)
tan_frame.pack(fill=X, pady=5)
Label(tan_frame, text="TAN:").pack(side=LEFT)
tan_entry = Entry(tan_frame, width=10)
tan_entry.insert(0, "HYDH01739D")
tan_entry.pack(side=LEFT, fill=X, expand=True)

def validate_tan_format(*args):
    value = tan_entry.get().upper()
    new_value = ""
    
    # Process each character based on its position
    for i, char in enumerate(value):
        if i < 4:  # First 4 positions must be letters
            if char.isalpha():
                new_value += char
        elif i < 9:  # Next 5 positions must be digits
            if char.isdigit():
                new_value += char
        elif i == 9:  # Last position must be a letter
            if char.isalpha():
                new_value += char
    
    # Limit to 10 characters
    new_value = new_value[:10]
    
    tan_entry.delete(0, END)
    tan_entry.insert(0, new_value)

# Bind to both KeyRelease and FocusOut events
tan_entry.bind('<KeyRelease>', validate_tan_format)
tan_entry.bind('<FocusOut>', validate_tan_format)

# Form Type Section
form_frame = Frame(main_frame)
form_frame.pack(fill=X, pady=5)
Label(form_frame, text="Form Type:").pack(side=LEFT)
form_type_var = StringVar(value="TDS - Salary - Form 24Q")
form_type_menu = OptionMenu(form_frame, form_type_var, 
    "TDS - Salary - Form 24Q",
    "TDS - Non Salary - Form 26Q", 
    "TDS - Non Salary - Non Resident - Form 27Q",
    "TCS - Form 27EQ",
    "All Form types")
form_type_menu.pack(side=LEFT, fill=X, expand=True)

# AIN Section
ain_frame = Frame(main_frame)
ain_frame.pack(fill=X, pady=5)
Label(ain_frame, text="AIN:").pack(side=LEFT)
ain_entry = Entry(ain_frame)
ain_entry.insert(0, "1019491")
ain_entry.pack(side=LEFT, fill=X, expand=True)

# From Date Section
from_date_frame = Frame(main_frame)
from_date_frame.pack(fill=X, pady=5)
Label(from_date_frame, text="From Month & Year:").pack(side=LEFT)
from_month_var = StringVar(value=datetime.now().strftime("%B"))
from_month_menu = OptionMenu(from_date_frame, from_month_var, *[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"])
from_month_menu.pack(side=LEFT, padx=5)
from_year_var = StringVar(value=str(datetime.now().year))
from_year_menu = OptionMenu(from_date_frame, from_year_var, *[str(y) for y in range(datetime.now().year - 5, datetime.now().year + 6)])
from_year_menu.pack(side=LEFT)

def update_to_date(*args):
    # Get current from date values
    from_month = from_month_var.get()
    from_year = int(from_year_var.get())
    
    # Convert month name to number (1-12)
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    from_month_num = months.index(from_month) + 1
    
    # Calculate to date (2 months later)
    to_month_num = from_month_num + 2
    to_year = from_year
    
    # Handle year rollover
    if to_month_num > 12:
        to_month_num -= 12
        to_year += 1
    
    # Update to date variables
    to_month_var.set(months[to_month_num - 1])
    to_year_var.set(str(to_year))

# Bind the update function to both from date variables
from_month_var.trace_add("write", update_to_date)
from_year_var.trace_add("write", update_to_date)

# To Date Section
to_date_frame = Frame(main_frame)
to_date_frame.pack(fill=X, pady=5)
Label(to_date_frame, text="To Month & Year:").pack(side=LEFT)
to_month_var = StringVar()
to_month_menu = OptionMenu(to_date_frame, to_month_var, *[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"])
to_month_menu.pack(side=LEFT, padx=5)
to_year_var = StringVar()
to_year_menu = OptionMenu(to_date_frame, to_year_var, *[str(y) for y in range(datetime.now().year - 5, datetime.now().year + 6)])
to_year_menu.pack(side=LEFT)

# Initialize to date based on from date
update_to_date()

# CAPTCHA Section
captcha_frame = Frame(main_frame)
captcha_frame.pack(fill=X, pady=5)
Label(captcha_frame, text="Enter CAPTCHA (visible in browser):").pack(side=LEFT)
captcha_entry = Entry(captcha_frame)
captcha_entry.pack(side=LEFT, fill=X, expand=True)

# Add validation to convert input to uppercase
def convert_to_uppercase(*args):
    value = captcha_entry.get()
    captcha_entry.delete(0, END)
    captcha_entry.insert(0, value.upper())

captcha_entry.bind('<KeyRelease>', convert_to_uppercase)

# Default amount section
# default_amount_frame = Frame(main_frame)
# default_amount_frame.pack(fill=X, pady=5)
# Label(default_amount_frame, text="Default Amount:").pack(side=LEFT)
# default_amount_entry = Entry(default_amount_frame)
# default_amount_entry.insert(0, "0")
# default_amount_entry.pack(side=LEFT, fill=X, expand=True)

# # Button to fill all fields with default amount
# def fill_with_default():
#     default_amount = default_amount_entry.get()
#     for _, entry, _ in amount_entries:
#         entry.delete(0, END)
#         entry.insert(0, default_amount)
#     print(f"Filled all amount fields with default amount: {default_amount}")

# Button(default_amount_frame, text="Fill All", command=fill_with_default).pack(side=RIGHT, padx=5)

# Buttons Section
button_frame = Frame(main_frame)
button_frame.pack(fill=X, pady=20)
Button(button_frame, text="Start (Open Browser & Fill Form)", 
       command=start_browser_and_fill_fields).pack(side=LEFT, padx=5)
Button(button_frame, text="Submit CAPTCHA", 
       command=submit_captcha).pack(side=LEFT, padx=5)
Button(button_frame, text="Extract BIN", 
       command=view_bin_data).pack(side=LEFT, padx=5)

# Status section
status_frame = Frame(main_frame)
status_frame.pack(fill=X, pady=10)
status_label = Label(status_frame, text="Status: Ready", fg="blue")
status_label.pack(side=LEFT)

# Update status function
def update_status(message, color="blue"):
    status_label.config(text=f"Status: {message}", fg=color)
    root.update_idletasks()

# Override print function to update status
original_print = print
def custom_print(*args, **kwargs):
    message = " ".join(map(str, args))
    update_status(message, "green" if "✅" in message else "blue")
    original_print(*args, **kwargs)

print = custom_print

root.mainloop()