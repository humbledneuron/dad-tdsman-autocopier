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

            print(f"❌ Attach ZIP error: {e}")


if __name__ == "__main__":

    app = IncomeTaxLoginAutomation()

    app.start_browser()

    app.navigate_to_upload_section()

    app.attach_tds_zip(
        zip_path=r"D:\GH\dad-tdsman-autocopier\mallaram test Q4\HZS24Q3.ZIP",
        quarter=None
    )

    input("Press ENTER to close...")

    app.close_browser()