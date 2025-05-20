import time
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
    
    form_type_dropdown = wait.until(EC.presence_of_element_located((By.NAME, "formtype")))
    Select(form_type_dropdown).select_by_visible_text(form_type)

    wait.until(EC.presence_of_element_located((By.NAME, "ain"))).send_keys(ain)

    Select(wait.until(EC.presence_of_element_located((By.NAME, "fmonth")))).select_by_visible_text(from_month)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "fyear")))).select_by_visible_text(from_year)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "tmonth")))).select_by_visible_text(to_month)
    Select(wait.until(EC.presence_of_element_located((By.NAME, "tyear")))).select_by_visible_text(to_year)

    print("Browser started and fields filled (excluding CAPTCHA).")

def submit_captcha_and_view_bin():
    global driver
    if not driver:
        print("Browser not launched yet.")
        return

    captcha = captcha_entry.get()
    try:
        driver.find_element(By.NAME, "captcha").send_keys(captcha)
        driver.find_element(By.XPATH, "//input[@value='View BIN Details']").click()
        print("CAPTCHA submitted. Button clicked.")
    except Exception as e:
        print(f"Error submitting CAPTCHA: {e}")


root = Tk()
root.title("BIN View Automation")
root.geometry("500x550")

Label(root, text="TAN:").pack()
tan_entry = Entry(root)
tan_entry.insert(0, "HYDZ03571B")
tan_entry.pack()

Label(root, text="Form Type:").pack()
form_type_var = StringVar(value="TDS - Salary - Form 24Q")
form_type_menu = OptionMenu(root, form_type_var, 
    "TDS - Salary - Form 24Q",
    "TDS - Non Salary - Form 26Q", 
    "TDS - Non Salary - Non Resident - Form 27Q",
    "TCS - Form 27EQ",
    "All Form types")
form_type_menu.pack()

Label(root, text="AIN:").pack()
ain_entry = Entry(root)
ain_entry.insert(0, "1019491")
ain_entry.pack()

Label(root, text="From Month & Year:").pack()
from_month_var = StringVar(value="April")
from_month_menu = OptionMenu(root, from_month_var, *["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
from_month_menu.pack()

from_year_var = StringVar(value="2023")
from_year_menu = OptionMenu(root, from_year_var, *[str(y) for y in range(2010, 2031)])
from_year_menu.pack()

Label(root, text="To Month & Year:").pack()
to_month_var = StringVar(value="June")
to_month_menu = OptionMenu(root, to_month_var, *["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
to_month_menu.pack()

to_year_var = StringVar(value="2023")
to_year_menu = OptionMenu(root, to_year_var, *[str(y) for y in range(2010, 2031)])
to_year_menu.pack()

Label(root, text="Enter CAPTCHA (visible in browser):").pack()
captcha_entry = Entry(root)
captcha_entry.pack()

Button(root, text="Start (Open Browser & Fill Form)", command=start_browser_and_fill_fields).pack(pady=10)
Button(root, text="Submit CAPTCHA & View BIN", command=submit_captcha_and_view_bin).pack(pady=10)

root.mainloop()
