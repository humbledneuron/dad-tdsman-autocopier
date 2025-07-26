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

class BinViewFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.driver = None
        self.amount_entries = []
        self._build_ui()

    def get_valid_chromedriver_path(self):
        path = ChromeDriverManager().install()
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
        else:
            raise RuntimeError(f"Invalid ChromeDriver binary at {path}. Please clear the webdriver_manager cache and try again.")

    def start_browser_and_fill_fields(self):
        tan = self.tan_entry.get()
        form_type = self.form_type_var.get()
        ain = self.ain_entry.get()
        from_month = self.from_month_var.get()
        from_year = self.from_year_var.get()
        to_month = self.to_month_var.get()
        to_year = self.to_year_var.get()

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        try:
            service = ChromeService(self.get_valid_chromedriver_path())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            self.print(f"Error initializing ChromeDriver: {e}")
            try:
                self.driver = webdriver.Chrome(options=options)
            except Exception as e:
                self.print(f"Fallback also failed: {e}")
                return
        self.driver.get("https://onlineservices.tin.egov-nsdl.com/TIN/JSP/etbaf/ViewBIN.jsp")
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "tan"))).send_keys(tan)
        Select(wait.until(EC.presence_of_element_located((By.NAME, "formtype")))).select_by_visible_text(form_type)
        wait.until(EC.presence_of_element_located((By.NAME, "ain"))).send_keys(ain)
        Select(wait.until(EC.presence_of_element_located((By.NAME, "fmonth")))).select_by_visible_text(from_month)
        Select(wait.until(EC.presence_of_element_located((By.NAME, "fyear")))).select_by_visible_text(from_year)
        Select(wait.until(EC.presence_of_element_located((By.NAME, "tmonth")))).select_by_visible_text(to_month)
        Select(wait.until(EC.presence_of_element_located((By.NAME, "tyear")))).select_by_visible_text(to_year)
        self.print("Browser started and fields filled (excluding CAPTCHA).")

    def submit_captcha(self):
        if not self.driver:
            self.print("Browser not launched yet.")
            return
        captcha = self.captcha_entry.get()
        try:
            self.driver.find_element(By.NAME, "captcha").send_keys(captcha)
            self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
            self.print("CAPTCHA submitted. Button clicked.")
            time.sleep(2)
            self.create_amount_fields()
        except Exception as e:
            self.print(f"Error submitting CAPTCHA: {e}")

    def create_amount_fields(self):
        try:
            self.clear_amount_fields()
            rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
            if not rows:
                self.print("No BIN records found to create amount fields.")
                return
            self.amounts_frame = LabelFrame(self.main_frame, text="Enter Amounts for Each Record", padx=10, pady=10)
            self.amounts_frame.pack(fill=X, pady=10)
            header_frame = Frame(self.amounts_frame)
            header_frame.pack(fill=X)
            Label(header_frame, text="Receipt No.", width=15).grid(row=0, column=0)
            Label(header_frame, text="Date", width=15).grid(row=0, column=1)
            Label(header_frame, text="Verification", width=15).grid(row=0, column=2)
            Label(header_frame, text="Amount", width=15).grid(row=0, column=3)
            ttk.Separator(self.amounts_frame, orient='horizontal').pack(fill=X, pady=5)
            for i, row in enumerate(rows):
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 9:
                    receipt_number = cols[3].text.strip()
                    date = cols[5].text.strip()
                    verification_alert = cols[9].text.strip() if len(cols) > 9 else "Not Verified"
                    entry_frame = Frame(self.amounts_frame)
                    entry_frame.pack(fill=X, pady=2)
                    Label(entry_frame, text=receipt_number, width=15).grid(row=0, column=0)
                    Label(entry_frame, text=date, width=15).grid(row=0, column=1)
                    verification_label = Label(entry_frame, text=verification_alert, width=15)
                    if verification_alert == "Amount Matches":
                        verification_label.configure(fg="green")
                    elif verification_alert == "Mismatch in Amount":
                        verification_label.configure(fg="red")
                    else:
                        verification_label.configure(fg="black")
                    verification_label.grid(row=0, column=2)
                    amount_entry = Entry(entry_frame, width=15)
                    amount_entry.grid(row=0, column=3)
                    amount_entry.insert(0, "")
                    self.amount_entries.append((i, amount_entry, verification_label))
            button_frame = Frame(self.amounts_frame)
            button_frame.pack(fill=X, pady=10)
            Button(button_frame, text="Apply Amounts & Check All Boxes", command=self.apply_amounts_and_check_boxes, bg="#4CAF50", fg="white").pack(side=LEFT, padx=5, fill=X, expand=True)
            Button(button_frame, text="Verify Amounts", command=self.verify_amounts, bg="#2196F3", fg="white").pack(side=LEFT, padx=5, fill=X, expand=True)
            Button(button_frame, text="Update Matching Amounts", command=self.update_matching_amounts, bg="#FF9800", fg="white").pack(side=LEFT, padx=5, fill=X, expand=True)
            self.print(f"Created {len(self.amount_entries)} amount entry fields for BIN records.")
        except Exception as e:
            self.print(f"Error creating amount fields: {e}")

    def clear_amount_fields(self):
        self.amount_entries = []
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, LabelFrame) and widget.cget("text") == "Enter Amounts for Each Record":
                widget.destroy()

    def apply_amounts_and_check_boxes(self):
        if not self.driver:
            self.print("Browser not launched yet.")
            return
        try:
            browser_amount_fields = self.driver.find_elements(By.XPATH, "//input[contains(@name, 'amt')]")
            checkboxes = self.driver.find_elements(By.XPATH, "//input[contains(@name, 'chk')]")
            amounts_applied = 0
            for idx, entry_field, _ in self.amount_entries:
                if idx < len(browser_amount_fields):
                    amount = entry_field.get()
                    if amount:
                        browser_amount_fields[idx].clear()
                        browser_amount_fields[idx].send_keys(amount)
                        amounts_applied += 1
            boxes_checked = 0
            for checkbox in checkboxes:
                if not checkbox.is_selected():
                    checkbox.click()
                    boxes_checked += 1
            self.print(f"✅ Applied {amounts_applied} amounts from GUI to browser and checked {boxes_checked} boxes.")
        except Exception as e:
            self.print(f"Error applying amounts and checking boxes: {e}")

    def verify_amounts(self):
        if not self.driver:
            self.print("Browser not launched yet.")
            return
        try:
            verify_button = self.driver.find_element(By.XPATH, "//input[@value='Verify Amount']")
            verify_button.click()
            self.print("Clicked 'Verify Amount' button. Waiting for verification...")
            time.sleep(2)
            self.update_verification_status()
        except Exception as e:
            self.print(f"Error verifying amounts: {e}")

    def update_verification_status(self):
        try:
            rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
            if not rows:
                self.print("No BIN records found to update verification status.")
                return
            matches_found = 0
            mismatches_found = 0
            for i, row in enumerate(rows):
                if i < len(self.amount_entries):
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 10:
                        verification_alert = cols[9].text.strip()
                        _, _, verification_label = self.amount_entries[i]
                        verification_label.config(text=verification_alert)
                        if verification_alert == "Amount Matches":
                            verification_label.config(fg="green")
                            matches_found += 1
                        elif verification_alert == "Mismatch in Amount":
                            verification_label.config(fg="red")
                            mismatches_found += 1
            self.print(f"Verification complete: {matches_found} matches, {mismatches_found} mismatches.")
        except Exception as e:
            self.print(f"Error updating verification status: {e}")

    def update_matching_amounts(self):
        try:
            rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
            if not rows:
                self.print("No BIN records found to update matching amounts.")
                return
            matches_updated = 0
            for i, row in enumerate(rows):
                if i < len(self.amount_entries):
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 10:
                        verification_alert = cols[9].text.strip()
                        if verification_alert == "Amount Matches":
                            try:
                                amount_field = cols[7].find_element(By.TAG_NAME, "input")
                                existing_amount = amount_field.get_attribute("value")
                                if existing_amount:
                                    idx, entry_field, _ = self.amount_entries[i]
                                    entry_field.delete(0, END)
                                    entry_field.insert(0, existing_amount)
                                    entry_field.config(bg="#e6ffe6")
                                    matches_updated += 1
                            except:
                                pass
            self.print(f"✅ Updated {matches_updated} matching amounts in the GUI.")
        except Exception as e:
            self.print(f"Error updating matching amounts: {e}")

    def view_bin_data(self):
        if not self.driver:
            self.print("Browser not launched yet.")
            return
        time.sleep(3)
        self.extract_bin_data()

    def extract_bin_data(self):
        try:
            rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'tabledetails')]")
            data_list = []
            for i, row in enumerate(rows):
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 9:
                    record = {
                        "Receipt Number": cols[3].text.strip(),
                        "DDO Serial No.": cols[4].text.strip(),
                        "Date": cols[5].text.strip(),
                    }
                    if i < len(self.amount_entries):
                        _, entry_field, _ = self.amount_entries[i]
                        amount = entry_field.get()
                        record["Amount"] = amount if amount else ""
                    else:
                        record["Amount"] = ""
                    data_list.append(record)
            if not data_list:
                self.print("No BIN records found.")
                return
            csv_file = "bin_table_data.csv"
            with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=data_list[0].keys())
                writer.writeheader()
                writer.writerows(data_list)
            self.print(f"\n✅ BIN data saved to CSV: {os.path.abspath(csv_file)}")
        except Exception as e:
            self.print(f"Error extracting table data: {e}")

    def _build_ui(self):
        self.root = self.winfo_toplevel()
        self.root.title("BIN View Automation")
        self.root.geometry("700x800")
        self.main_frame_container = Frame(self)
        self.main_frame_container.pack(expand=True, fill=BOTH)
        self.scrollbar = Scrollbar(self.main_frame_container)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self.main_frame_container, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        self.main_frame = Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor='nw')
        def configure_canvas(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=event.width)
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind('<Configure>', configure_canvas)
        self.main_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.main_frame.configure(padx=20, pady=20)
        tan_frame = Frame(self.main_frame)
        tan_frame.pack(fill=X, pady=5)
        Label(tan_frame, text="TAN:").pack(side=LEFT)
        self.tan_entry = Entry(tan_frame, width=10)
        self.tan_entry.insert(0, "HYDH01739D")
        self.tan_entry.pack(side=LEFT, fill=X, expand=True)
        def validate_tan_format(*args):
            value = self.tan_entry.get().upper()
            new_value = ""
            for i, char in enumerate(value):
                if i < 4:
                    if char.isalpha():
                        new_value += char
                elif i < 9:
                    if char.isdigit():
                        new_value += char
                elif i == 9:
                    if char.isalpha():
                        new_value += char
            new_value = new_value[:10]
            self.tan_entry.delete(0, END)
            self.tan_entry.insert(0, new_value)
        self.tan_entry.bind('<KeyRelease>', validate_tan_format)
        self.tan_entry.bind('<FocusOut>', validate_tan_format)
        form_frame = Frame(self.main_frame)
        form_frame.pack(fill=X, pady=5)
        Label(form_frame, text="Form Type:").pack(side=LEFT)
        self.form_type_var = StringVar(value="TDS - Salary - Form 24Q")
        form_type_menu = OptionMenu(form_frame, self.form_type_var, "TDS - Salary - Form 24Q", "TDS - Non Salary - Form 26Q", "TDS - Non Salary - Non Resident - Form 27Q", "TCS - Form 27EQ", "All Form types")
        form_type_menu.pack(side=LEFT, fill=X, expand=True)
        ain_frame = Frame(self.main_frame)
        ain_frame.pack(fill=X, pady=5)
        Label(ain_frame, text="AIN:").pack(side=LEFT)
        self.ain_entry = Entry(ain_frame)
        self.ain_entry.insert(0, "1019491")
        self.ain_entry.pack(side=LEFT, fill=X, expand=True)
        from_date_frame = Frame(self.main_frame)
        from_date_frame.pack(fill=X, pady=5)
        Label(from_date_frame, text="From Month & Year:").pack(side=LEFT)
        self.from_month_var = StringVar(value=datetime.now().strftime("%B"))
        from_month_menu = OptionMenu(from_date_frame, self.from_month_var, *[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"])
        from_month_menu.pack(side=LEFT, padx=5)
        self.from_year_var = StringVar(value=str(datetime.now().year))
        from_year_menu = OptionMenu(from_date_frame, self.from_year_var, *[str(y) for y in range(datetime.now().year - 5, datetime.now().year + 6)])
        from_year_menu.pack(side=LEFT)
        def update_to_date(*args):
            from_month = self.from_month_var.get()
            from_year = int(self.from_year_var.get())
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            from_month_num = months.index(from_month) + 1
            to_month_num = from_month_num + 2
            to_year = from_year
            if to_month_num > 12:
                to_month_num -= 12
                to_year += 1
            self.to_month_var.set(months[to_month_num - 1])
            self.to_year_var.set(str(to_year))
        self.from_month_var.trace_add("write", update_to_date)
        self.from_year_var.trace_add("write", update_to_date)
        to_date_frame = Frame(self.main_frame)
        to_date_frame.pack(fill=X, pady=5)
        Label(to_date_frame, text="To Month & Year:").pack(side=LEFT)
        self.to_month_var = StringVar()
        to_month_menu = OptionMenu(to_date_frame, self.to_month_var, *[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"])
        to_month_menu.pack(side=LEFT, padx=5)
        self.to_year_var = StringVar()
        to_year_menu = OptionMenu(to_date_frame, self.to_year_var, *[str(y) for y in range(datetime.now().year - 5, datetime.now().year + 6)])
        to_year_menu.pack(side=LEFT)
        update_to_date()
        captcha_frame = Frame(self.main_frame)
        captcha_frame.pack(fill=X, pady=5)
        Label(captcha_frame, text="Enter CAPTCHA (visible in browser):").pack(side=LEFT)
        self.captcha_entry = Entry(captcha_frame)
        self.captcha_entry.pack(side=LEFT, fill=X, expand=True)
        def convert_to_uppercase(*args):
            value = self.captcha_entry.get()
            self.captcha_entry.delete(0, END)
            self.captcha_entry.insert(0, value.upper())
        self.captcha_entry.bind('<KeyRelease>', convert_to_uppercase)
        button_frame = Frame(self.main_frame)
        button_frame.pack(fill=X, pady=20)
        Button(button_frame, text="Start (Open Browser & Fill Form)", command=self.start_browser_and_fill_fields).pack(side=LEFT, padx=5)
        Button(button_frame, text="Submit CAPTCHA", command=self.submit_captcha).pack(side=LEFT, padx=5)
        Button(button_frame, text="Extract BIN", command=self.view_bin_data).pack(side=LEFT, padx=5)
        status_frame = Frame(self.main_frame)
        status_frame.pack(fill=X, pady=10)
        self.status_label = Label(status_frame, text="Status: Ready", fg="blue")
        self.status_label.pack(side=LEFT)
        def update_status(message, color="blue"):
            self.status_label.config(text=f"Status: {message}", fg=color)
            self.root.update_idletasks()
        self.update_status = update_status
        self.original_print = print
        def custom_print(*args, **kwargs):
            message = " ".join(map(str, args))
            self.update_status(message, "green" if "✅" in message else "blue")
            self.original_print(*args, **kwargs)
        self.print = custom_print