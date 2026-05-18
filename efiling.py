import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.ui import Select
from datetime import datetime
import os

class IncomeTaxLoginAutomation:

    def __init__(self):

        self.driver = None
    
    def safe_click(self, xpath, timeout=20):

        wait = WebDriverWait(self.driver, timeout)

        element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, xpath)
            )
        )

        # Scroll element into view
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

        # JS click is more stable on Angular portals
        self.driver.execute_script(
            "arguments[0].click();",
            element
        )

        return element
        
    def start_browser(self):

        try:

            options = uc.ChromeOptions()

            options.add_argument("--start-maximized")

            # Dedicated Selenium profile
            options.add_argument(
                r"--user-data-dir=C:\selenium_profiles\income_tax"
            )

            # Helps reduce detection
            options.add_argument("--disable-blink-features=AutomationControlled")

            self.driver = uc.Chrome(
                options=options,
                use_subprocess=True
            )

            self.driver.get(
                "https://eportal.incometax.gov.in/iec/foservices/"
            )

            wait = WebDriverWait(self.driver, 30)

            wait.until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "body")
                )
            )

            print("✅ Portal opened successfully.")
            # time.sleep(15)

        except Exception as e:

            print(f"❌ Error: {e}")
    
    def navigate_to_upload_section(self):

        try:

            wait = WebDriverWait(self.driver, 20)

            actions = ActionChains(self.driver)

            # STEP 1
            print("STEP 1: Hovering e-File")

            # efile_menu = wait.until(
            #     EC.presence_of_element_located(
            #         (
            #             By.XPATH,
            #             '//*[@id="e-File"]/span[2]'
            #         )
            #     )
            # )
            # actions.move_to_element(efile_menu).perform()
            self.safe_click('//*[@id="e-File"]/span[2]')

            time.sleep(2)

            # STEP 2
            print("STEP 2: Hovering Income Tax Forms")

            # submenu = wait.until(
            #     EC.presence_of_element_located(
            #         (
            #             By.XPATH,
            #             '//*[@id="mat-menu-panel-22"]/div/span[1]/span/div/button/span/span'
            #         )
            #     )
            # )
            # actions.move_to_element(submenu).perform()
            self.safe_click('//*[@id="mat-menu-panel-22"]/div/span[1]/span/div/button/span/span')

            time.sleep(2)

            # STEP 3
            print("STEP 3: Clicking File Income Tax Forms")

            self.safe_click(
                '//*[@id="mat-menu-panel-28"]/div/span[1]/span/button/span/span'
            )

            time.sleep(4)

            # STEP 4
            print("STEP 4: Clicking tab")

            self.safe_click(
                '//*[@id="mat-tab-group-0-label-1"]'
            )

            time.sleep(3)

            # STEP 5
            print("STEP 5: Pagination")

            self.safe_click(
                '//*[@id="maincontentid"]/app-dashboard/app-file-income-tax-forms/div/mat-card/div/div/mat-paginator/div/div/div[2]/button[4]/span[3]'
            )

            time.sleep(3)

            # STEP 6
            print("STEP 6: Selecting form card")

            self.safe_click(
                '//*[@id="mat-tab-group-0-content-1"]/div/div/div/mat-card/div[11]/div/mat-card/mat-card-content/div/div[1]'
            )

            time.sleep(3)

            # STEP 7
            print("STEP 7: Let's get started")

            self.safe_click(
                '//*[@id="maincontentid"]/app-dashboard/app-file-income-tax-forms/app-instruction-screen/div/div[1]/div/div[1]/div[3]/div[2]/button'
            )

            print("✅ Navigation completed successfully.")

        except Exception as e:

            print(f"❌ Navigation error: {e}")
            
    def close_browser(self):

        if self.driver:

            self.driver.quit()

            print("✅ Browser closed.")


    def attach_tds_zip(
        self,
        zip_path,
        quarter="Q4"
    ):
        # =====================================
        # AUTO DETECT QUARTER FROM FILENAME
        # =====================================

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
        
        try:

            wait = WebDriverWait(self.driver, 20)

            # =====================================
            # STEP 1
            # FORM TYPE DROPDOWN
            # =====================================

            print("STEP 1: Opening form type dropdown")

            self.safe_click(
                "//mat-select[@id='formTypeCode']"
            )

            time.sleep(2)

            # =====================================
            # STEP 2
            # SELECT FORM 24Q
            # =====================================

            print("STEP 2: Selecting Form 24Q")

            self.safe_click(
                "//span[contains(text(),'24Q (Salary)')]"
            )

            time.sleep(2)

            # =====================================
            # STEP 3
            # GET TAN NUMBER
            # =====================================

            print("STEP 3: Fetching TAN")

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

            # =====================================
            # STEP 4
            # FINANCIAL YEAR DROPDOWN
            # =====================================

            print("STEP 4: Opening FY dropdown")

            self.safe_click(
                "//mat-select[@id='financialYear']"
            )

            time.sleep(2)

            # =====================================
            # STEP 5
            # SELECT LATEST FINANCIAL YEAR
            # =====================================

            current_year = datetime.now().year

            # Always use previous FY
            # Example:
            # 2026 -> 2025-26

            fy_start = current_year - 1

            fy_end = str(current_year)[-2:]

            financial_year = f"{fy_start}-{fy_end}"

            print(f"Selecting FY: {financial_year}")

            time.sleep(2)

            # Get all dropdown options
            fy_options = wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//mat-option//span"
                    )
                )
            )

            fy_found = False

            for option in fy_options:

                option_text = option.text.strip()

                print(f"Found FY option: {option_text}")

                if financial_year in option_text:

                    self.driver.execute_script(
                        "arguments[0].click();",
                        option
                    )

                    print(f"✅ Selected FY: {financial_year}")

                    fy_found = True

                    break

            if not fy_found:

                raise Exception(
                    f"Financial year {financial_year} not found"
                )

            # =====================================
            # STEP 6
            # QUARTER DROPDOWN
            # =====================================

            print("STEP 6: Opening quarter dropdown")

            self.safe_click(
                '//*[@id="mat-select-value-3"]/span/span'                
            )

            time.sleep(2)

            # =====================================
            # STEP 7
            # SELECT QUARTER
            # =====================================

            print(f"Selecting quarter: {quarter}")

            quarter_xpath = (
                f"//span[contains(text(),'{quarter}')]"
            )

            self.safe_click(quarter_xpath)

            time.sleep(2)

            # =====================================
            # STEP 8
            # SELECT REGULAR FILING TYPE
            # =====================================

            print("STEP 8: Selecting Regular filing")

            regular_radio = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[@type='radio' and @value='G']"
                    )
                )
            )

            self.driver.execute_script(
                "arguments[0].click();",
                regular_radio
            )

            print("✅ Regular filing selected.")

            # =====================================
            # STEP 9
            # ATTACH ZIP FILE
            # =====================================

            print("STEP 9: Uploading ZIP")

            # Convert to absolute path
            zip_path = os.path.abspath(zip_path)

            print(f"ZIP PATH: {zip_path}")

            if not os.path.exists(zip_path):

                raise Exception(
                    f"ZIP file not found: {zip_path}"
                )

            # REAL hidden file input
            upload_input = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "fileInputdocId"
                    )
                )
            )

            # Upload directly
            upload_input.send_keys(zip_path)

            print("✅ ZIP attached successfully.")

            wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[contains(text(),'Attach')]"
                    )
                )
            )

            print("✅ Upload completed.")

            print(upload_input.get_attribute("value"))
        
            # =====================================
            # STEP 10
            # PROCEED TO E-VERIFY
            # =====================================

            print("STEP 10: Proceeding to e-Verify")

            self.safe_click(
                "//button[contains(text(),'Proceed to e-Verify')]"
            )

            print("✅ Clicked Proceed to e-Verify")

            # =====================================
            # STEP 11
            # CONFIRM E-VERIFY POPUP
            # =====================================

            print("STEP 11: Confirming e-Verify popup")

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

            # =====================================
            # STEP 12
            # SELECT AADHAAR OTP OPTION
            # =====================================

            print("STEP 12: Selecting Aadhaar OTP verification")

            aadhaar_radio = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[@type='radio' and @value='verifyUsingNewOTP']"
                        ## if in case above doesn't work
                        # "//input[@value='verifyUsingNewOTP']"
                    )
                )
            )

            self.driver.execute_script(
                "arguments[0].click();",
                aadhaar_radio
            )
            
            ## and this 
            # Normal click first
            # aadhaar_radio.click()
            # time.sleep(2)

            print("✅ Aadhaar OTP option selected.")

            # =====================================
            # STEP 13
            # CLICK CONTINUE
            # =====================================

            print("STEP 13: Waiting for Continue button")

            continue_button = wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "eVerifySelectOptionContinueBtn"
                    )
                )
            )

            # Scroll into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                continue_button
            )

            time.sleep(2)

            # Wait until enabled
            wait.until(
                lambda d: continue_button.is_enabled()
            )

            print(continue_button.get_attribute("disabled"))

            print("STEP 13: Clicking Continue")

            self.driver.execute_script(
                "arguments[0].click();",
                continue_button
            )

            print("✅ Continue clicked.")
        
            # =====================================
            # STEP 14
            # CHECK AADHAAR CONSENT
            # =====================================

            print("STEP 14: Checking Aadhaar consent")

            checkbox = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//label[contains(text(),'I agree to validate my Aadhaar Details')]"
                    )
                )
            )

            # Scroll into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                checkbox
            )

            time.sleep(1)

            # Native click
            checkbox.click()

            time.sleep(2)

            print("✅ Aadhaar consent checked.")

            
            # =====================================
            # STEP 15
            # GENERATE AADHAAR OTP
            # =====================================

            print("STEP 15: Waiting for Generate OTP button")

            generate_otp_button = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[contains(text(),'Generate Aadhaar OTP')]"
                    )
                )
            )

            # Wait until enabled
            wait.until(
                lambda d: generate_otp_button.is_enabled()
            )

            time.sleep(1)

            print("STEP 15: Clicking Generate OTP")

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