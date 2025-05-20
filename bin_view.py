import time
import csv
import os
from tkinter import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = None

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
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
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
    except Exception as e:
        print(f"Error submitting CAPTCHA: {e}")

def view_bin_data():
    global driver
    if not driver:
        print("Browser not launched yet.")
        return
        
    time.sleep(3)
    extract_bin_data()

def extract_bin_data():
    global driver
    try:
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
        data_list = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 9:
                record = {
                    # "Sr No.": cols[0].text.strip(),
                    "AIN": cols[1].text.strip(),
                    # "AO Name": cols[2].text.strip(),
                    "Receipt Number": cols[3].text.strip(),
                    "DDO Serial No.": cols[4].text.strip(),
                    "Date": cols[5].text.strip(),
                    # "Nature of Payment": cols[6].text.strip(),
                    # "Amount": cols[7].text.strip(),
                    "Check": "checked" if cols[8].find_element(By.TAG_NAME, "input").is_selected() else "unchecked"
                }
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
root.geometry("500x600")

# Create main frame for better organization
main_frame = Frame(root, padx=20, pady=20)
main_frame.pack(expand=True, fill=BOTH)

# TAN Section
tan_frame = Frame(main_frame)
tan_frame.pack(fill=X, pady=5)
Label(tan_frame, text="TAN:").pack(side=LEFT)
tan_entry = Entry(tan_frame)
tan_entry.insert(0, "HYDZ03571B")
tan_entry.pack(side=LEFT, fill=X, expand=True)

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
from_month_var = StringVar(value="April")
from_month_menu = OptionMenu(from_date_frame, from_month_var, *[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"])
from_month_menu.pack(side=LEFT, padx=5)
from_year_var = StringVar(value="2023")
from_year_menu = OptionMenu(from_date_frame, from_year_var, *[str(y) for y in range(2010, 2031)])
from_year_menu.pack(side=LEFT)

# To Date Section
to_date_frame = Frame(main_frame)
to_date_frame.pack(fill=X, pady=5)
Label(to_date_frame, text="To Month & Year:").pack(side=LEFT)
to_month_var = StringVar(value="June")
to_month_menu = OptionMenu(to_date_frame, to_month_var, *[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"])
to_month_menu.pack(side=LEFT, padx=5)
to_year_var = StringVar(value="2023")
to_year_menu = OptionMenu(to_date_frame, to_year_var, *[str(y) for y in range(2010, 2031)])
to_year_menu.pack(side=LEFT)

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

# Buttons Section
button_frame = Frame(main_frame)
button_frame.pack(fill=X, pady=20)
Button(button_frame, text="Start (Open Browser & Fill Form)", 
       command=start_browser_and_fill_fields).pack(side=LEFT, padx=5)
Button(button_frame, text="Submit CAPTCHA", 
       command=submit_captcha).pack(side=LEFT, padx=5)
Button(button_frame, text="Extract BIN", 
       command=view_bin_data).pack(side=LEFT, padx=5)

root.mainloop()
