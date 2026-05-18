import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime

import time
import os


class IncomeTaxLoginAutomation:

    def __init__(self):

        self.driver = None


    def enter_user_id(
        self,
        user_id
    ):

        try:

            wait = WebDriverWait(self.driver, 15)

            print("Entering User ID")

            user_input = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "panAdhaarUserId"
                    )
                )
            )

            user_input.clear()

            user_input.send_keys(user_id)

            time.sleep(0.5)

            # Press ENTER
            user_input.send_keys("\n")

            print("✅ User ID submitted.")

        except Exception as e:

            print(f"❌ User ID error: {e}")

    def enter_password(
        self,
        password,
        max_retries=7
    ):

        try:

            wait = WebDriverWait(self.driver, 15)

            print("Checking secure access checkbox")

            # =====================================================
            # CHECKBOX
            # =====================================================

            checkbox = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//label[contains(.,'Please confirm your secure access message')]"
                    )
                )
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                checkbox
            )

            time.sleep(0.5)

            # Native click works better here
            checkbox.click()

            time.sleep(1)

            print("✅ Checkbox checked.")

            # =====================================================
            # PASSWORD INPUT
            # =====================================================

            password_input = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "loginPasswordField"
                    )
                )
            )

            password_input.clear()

            password_input.send_keys(password)

            time.sleep(0.5)

            # =====================================================
            # CONTINUE BUTTON
            # =====================================================

            continue_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(.,'Continue')]"
                    )
                )
            )

            # =====================================================
            # RETRY LOOP
            # =====================================================

            for attempt in range(max_retries):

                print(
                    f"Password submit attempt: {attempt + 1}"
                )

                self.driver.execute_script(
                    "arguments[0].click();",
                    continue_button
                )

                time.sleep(2)

                page_source = self.driver.page_source

                # ===============================================
                # WRONG PASSWORD
                # ===============================================

                if (
                    "Invalid Password, Please retry"
                    in page_source
                ):

                    raise Exception(
                        "❌ Invalid password."
                    )

                # ===============================================
                # REQUEST NOT AUTHENTICATED
                # ===============================================

                if (
                    "Request is not authenticated"
                    in page_source
                ):

                    print(
                        "⚠️ Request not authenticated. Retrying..."
                    )

                    time.sleep(1)

                    continue

                # ===============================================
                # SUCCESS
                # ===============================================

                print("✅ Password accepted.")

                return True

            raise Exception(
                "❌ Max retries reached."
            )

        except Exception as e:

            print(f"❌ Password error: {e}")

            return False

    # =========================================================
    # GENERIC HELPERS
    # =========================================================
    def wait_for_loader_to_disappear(self, timeout=30):

        try:

            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        (
                            "//mat-spinner | "
                            "//div[contains(@class,'loader')] | "
                            "//div[contains(@class,'spinner')] | "
                            "//div[contains(@class,'overlay')]"
                        )
                    )
                )
            )

            print("✅ Loader disappeared.")

        except Exception:
            timestamp = int(time.time())
            self.driver.save_screenshot(
                f"error_{timestamp}.png"
            )

            print("⚠️ No loader detected or loader timeout.")

    def safe_click(self, xpath, timeout=20):

        wait = WebDriverWait(self.driver, timeout)

        element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, xpath)
            )
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )

        time.sleep(1)

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath)
            )
        )

        self.driver.execute_script(
            "arguments[0].click();",
            element
        )

        return element

    def click_button_by_text(
        self,
        button_text,
        timeout=20
    ):

        print(f"Clicking button: {button_text}")

        button = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//button[contains(text(),'{button_text}')]"
                )
            )
        )

        self.driver.execute_script(
            "arguments[0].click();",
            button
        )

        print(f"✅ Clicked button: {button_text}")

    def select_dropdown_option(
        self,
        dropdown_xpath,
        option_text,
        timeout=10
    ):

        print(f"Selecting dropdown option: {option_text}")

        # Open dropdown
        self.safe_click(dropdown_xpath)

        # SMALL wait only
        time.sleep(0.3)

        option_xpath = (
            f"//mat-option//span[contains(text(),'{option_text}')]"
        )

        option = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, option_xpath)
            )
        )

        self.driver.execute_script(
            "arguments[0].click();",
            option
        )

        print(f"✅ Selected: {option_text}")

    def select_radio_by_value(
        self,
        value,
        timeout=10
    ):

        print(f"Selecting radio: {value}")

        radio = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//input[@type='radio' and @value='{value}']"
                )
            )
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            radio
        )

        time.sleep(0.5)

        # JS click works better here
        self.driver.execute_script(
            "arguments[0].click();",
            radio
        )

        print(f"✅ Radio selected: {value}")

    def check_checkbox_by_label(
        self,
        label_text,
        timeout=20
    ):

        print(f"Checking checkbox: {label_text}")

        checkbox = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//label[contains(text(),'{label_text}')]"
                )
            )
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            checkbox
        )

        time.sleep(1)

        checkbox.click()

        print(f"✅ Checkbox checked: {label_text}")

    # =========================================================
    # BROWSER
    # =========================================================
    def start_browser(self):

        try:

            options = uc.ChromeOptions()

            options.add_argument("--start-maximized")

            options.add_argument(
                r"--user-data-dir=C:\selenium_profiles\income_tax"
            )

            options.add_argument(
                "--disable-blink-features=AutomationControlled"
            )

            self.driver = uc.Chrome(
                options=options,
                use_subprocess=True
            )

            self.driver.get(
                "https://eportal.incometax.gov.in/iec/foservices/"
            )

            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "body")
                )
            )

            print("✅ Portal opened successfully.")

        except Exception as e:
            timestamp = int(time.time())
            self.driver.save_screenshot(
                f"error_{timestamp}.png"
            )

            print(f"❌ Error: {e}")

    def close_browser(self):

        if self.driver:

            self.driver.quit()

            print("✅ Browser closed.")

    # =========================================================
    # NAVIGATION
    # =========================================================
    def navigate_to_upload_section(self):

        try:

            print("STEP 1: e-File")

            self.safe_click(
                '//*[@id="e-File"]/span[2]'
            )

            time.sleep(2)

            print("STEP 2: Income Tax Forms")

            self.safe_click(
                '//*[@id="mat-menu-panel-22"]/div/span[1]/span/div/button/span/span'
            )

            time.sleep(2)

            print("STEP 3: File Income Tax Forms")

            self.safe_click(
                '//*[@id="mat-menu-panel-28"]/div/span[1]/span/button/span/span'
            )

            time.sleep(4)

            print("STEP 4: Tab")

            self.safe_click(
                '//*[@id="mat-tab-group-0-label-1"]'
            )

            time.sleep(3)

            print("STEP 5: Pagination")

            self.safe_click(
                '//*[@id="maincontentid"]/app-dashboard/app-file-income-tax-forms/div/mat-card/div/div/mat-paginator/div/div/div[2]/button[4]/span[3]'
            )

            time.sleep(3)

            print("STEP 6: Select Form Card")

            self.safe_click(
                '//*[@id="mat-tab-group-0-content-1"]/div/div/div/mat-card/div[11]/div/mat-card/mat-card-content/div/div[1]'
            )

            time.sleep(3)

            print("STEP 7: Get Started")

            self.safe_click(
                '//*[@id="maincontentid"]/app-dashboard/app-file-income-tax-forms/app-instruction-screen/div/div[1]/div/div[1]/div[3]/div[2]/button'
            )

            print("✅ Navigation completed.")

        except Exception as e:
            timestamp = int(time.time())
            self.driver.save_screenshot(
                f"error_{timestamp}.png"
            )

            print(f"❌ Navigation error: {e}")

    # =========================================================
    # MAIN TDS FLOW
    # =========================================================
    def attach_tds_zip(
        self,
        zip_path,
        quarter=None
    ):

        try:

            wait = WebDriverWait(self.driver, 20)

            # =====================================================
            # AUTO DETECT QUARTER
            # =====================================================

            filename = os.path.basename(zip_path).upper()

            if not quarter:

                if "Q1" in filename:

                    quarter = "Q1"

                elif "Q2" in filename:

                    quarter = "Q2"

                elif "Q3" in filename:

                    quarter = "Q3"

                elif "Q4" in filename:

                    quarter = "Q4"

                else:

                    raise Exception(
                        "Could not detect quarter from filename"
                    )

            print(f"Detected Quarter: {quarter}")

            # =====================================================
            # FORM TYPE
            # =====================================================

            self.select_dropdown_option(
                "//mat-select[@id='formTypeCode']",
                "24Q (Salary)"
            )

            # =====================================================
            # TAN
            # =====================================================

            tan_element = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="maincontentid"]/app-dashboard/app-file-income-tax-forms/app-formtdsreturns/div[2]/mat-card/div[4]/div'
                    )
                )
            )

            tan_number = tan_element.text.strip()

            print(f"✅ TAN Number: {tan_number}")

            # =====================================================
            # FINANCIAL YEAR
            # =====================================================

            current_year = datetime.now().year

            fy_start = current_year - 1

            fy_end = str(current_year)[-2:]

            financial_year = f"{fy_start}-{fy_end}"

            print(f"Selecting FY: {financial_year}")

            self.select_dropdown_option(
                "//mat-select[@id='financialYear']",
                financial_year
            )

            # =====================================================
            # QUARTER
            # =====================================================

            self.select_dropdown_option(
                '//*[@id="mat-select-value-3"]/span/span',
                quarter
            )

            # =====================================================
            # REGULAR RADIO
            # =====================================================

            self.select_radio_by_value("G")

            # =====================================================
            # ZIP VALIDATION
            # =====================================================

            zip_path = os.path.abspath(zip_path)

            print(f"ZIP PATH: {zip_path}")

            if not os.path.exists(zip_path):

                raise Exception(
                    f"ZIP file not found: {zip_path}"
                )

            # =====================================================
            # ZIP UPLOAD
            # =====================================================

            print("Uploading ZIP")

            upload_input = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "fileInputdocId"
                    )
                )
            )

            upload_input.send_keys(zip_path)

            print("✅ ZIP attached successfully.")

            # =====================================================
            # PROCEED TO E-VERIFY
            # =====================================================

            self.click_button_by_text(
                "Proceed to e-Verify"
            )

            # =====================================================
            # CONFIRM POPUP
            # =====================================================

            confirm_button = wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'modal-content')]//button[contains(text(),'Yes')]"
                    )
                )
            )

            self.driver.execute_script(
                "arguments[0].click();",
                confirm_button
            )

            print("✅ e-Verify confirmation accepted.")

            # =====================================================
            # OTP RADIO
            # =====================================================

            self.select_radio_by_value(
                "verifyUsingNewOTP"
            )

            # =====================================================
            # CONTINUE
            # =====================================================

            continue_button = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "eVerifySelectOptionContinueBtn"
                    )
                )
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                continue_button
            )

            time.sleep(2)

            wait.until(
                lambda d: continue_button.is_enabled()
            )

            self.driver.execute_script(
                "arguments[0].click();",
                continue_button
            )

            print("✅ Continue clicked.")

            # =====================================================
            # AADHAAR CONSENT
            # =====================================================

            self.check_checkbox_by_label(
                "I agree to validate my Aadhaar Details"
            )

            # =====================================================
            # GENERATE OTP
            # =====================================================

            generate_otp_button = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[contains(text(),'Generate Aadhaar OTP')]"
                    )
                )
            )

            wait.until(
                lambda d: generate_otp_button.is_enabled()
            )

            time.sleep(1)

            self.driver.execute_script(
                "arguments[0].click();",
                generate_otp_button
            )

            print("✅ Aadhaar OTP generated.")

        except Exception as e:

            timestamp = int(time.time())
            self.driver.save_screenshot(
                f"error_{timestamp}.png"
            )

            print(f"❌ Attach ZIP error: {e}")


if __name__ == "__main__":

    app = IncomeTaxLoginAutomation()

    app.start_browser()

    app.enter_user_id("HYDG06231B")

    app.enter_password("HYDG06231b*1")

    app.navigate_to_upload_section()

    app.attach_tds_zip(
        zip_path=r"D:\GH\dad-tdsman-autocopier\mallaram test Q4\HZS24Q3.ZIP",
        quarter=None
    )

    input("Press ENTER to close...")

    app.close_browser()


import tkinter as tk
from tkinter import ttk
import glob
import re


class EfilingFrame(ttk.Frame):

    def __init__(
        self,
        parent,
        shared_excel_entry,
        shared_log_text=None
    ):

        super().__init__(parent)
        self.automation = IncomeTaxLoginAutomation()

        self.shared_excel_entry = shared_excel_entry
        self.shared_log_text = shared_log_text

        self._build_ui()

    def start_efiling_process(self):

        try:

            username = self.efiling_username_var.get()
            password = self.efiling_password_var.get()
            zip_path = self.zip_var.get()

            if not username:
                print("No eFiling username found.")
                return

            if not password:
                print("No eFiling password found.")
                return

            if not zip_path or not os.path.exists(zip_path):
                print("ZIP file not found.")
                return

            print("Starting eFiling automation...")

            self.close_browser()
            self.automation.start_browser()

            self.automation.enter_user_id(username)

            password_success = self.automation.enter_password(password)

            if not password_success:
                print("Password step failed.")
                return

            self.automation.navigate_to_upload_section()

            self.automation.attach_tds_zip(zip_path)

            print("✅ eFiling automation completed.")

        except Exception as e:

            print(f"eFiling process error: {e}")

    def auto_detect_zip(self):

        try:

            excel_path = self.shared_excel_entry.get()

            if not excel_path:
                return

            folder = os.path.dirname(excel_path)

            zip_files = glob.glob(
                os.path.join(folder, "*.zip")
            )

            matched_zip = None

            for file in zip_files:

                filename = os.path.basename(file).upper()

                if re.search(r"[A-Z]{3}\d{2}Q[1-4]", filename):

                    matched_zip = file
                    break

            if matched_zip:

                self.zip_var.set(matched_zip)

        except Exception as e:

            print(f"ZIP detection error: {e}")

    def _build_ui(self):

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ==========================================
        # USERNAME
        # ==========================================

        ttk.Label(
            main_frame,
            text="eFiling Username:"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.efiling_username_var = tk.StringVar()

        username_entry = ttk.Entry(
            main_frame,
            textvariable=self.efiling_username_var,
            state="readonly",
            width=40
        )

        username_entry.grid(row=0, column=1, pady=5, sticky="ew")

        # ==========================================
        # PASSWORD
        # ==========================================

        ttk.Label(
            main_frame,
            text="eFiling Password:"
        ).grid(row=1, column=0, sticky="w", pady=5)

        self.efiling_password_var = tk.StringVar()

        password_entry = ttk.Entry(
            main_frame,
            textvariable=self.efiling_password_var,
            state="readonly",
            width=40
        )

        password_entry.grid(row=1, column=1, pady=5, sticky="ew")

        # ==========================================
        # ZIP FILE
        # ==========================================

        ttk.Label(
            main_frame,
            text="ZIP File:"
        ).grid(row=2, column=0, sticky="w", pady=5)

        self.zip_var = tk.StringVar()

        zip_entry = ttk.Entry(
            main_frame,
            textvariable=self.zip_var,
            state="readonly",
            width=60
        )

        zip_entry.grid(row=2, column=1, pady=5, sticky="ew")

        main_frame.columnconfigure(1, weight=1)

        # ==========================================
        # BUTTON FRAME
        # ==========================================

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(
            row=3,
            column=1,
            sticky="e",
            pady=20
        )

        # START BUTTON
        start_button = ttk.Button(
            button_frame,
            text="Start eFiling",
            command=self.start_efiling_process
        )

        start_button.pack(side="left", padx=5)


        # CLOSE BUTTON
        close_button = ttk.Button(
            button_frame,
            text="Close Browser",
            command=self.close_browser
        )

        close_button.pack(side="left", padx=5)


    def close_browser(self):

        try:

            if self.automation:

                self.automation.close_browser()

                print("Browser closed successfully.")

        except Exception as e:

            print(f"Close browser error: {e}")






