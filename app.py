from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from dotenv import load_dotenv
import platform
import os

load_dotenv()

selenium_profile = os.path.join(os.getcwd(), "selenium_profile")
os.makedirs(selenium_profile, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={selenium_profile}")
chrome_options.add_argument("--profile-directory=Default")  # Optional
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--no-default-browser-check")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")

driver_binary = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
if platform.system() != "Windows":
    # If chromedriver isn't in the current directory, try system path
    if not os.path.exists(driver_binary):
        driver_binary = "/opt/homebrew/bin/chromedriver"  # default brew path
    os.system(f"chmod +x {driver_binary}")
service = Service(driver_binary)

driver = webdriver.Chrome(service=service, options=chrome_options)
print("-------------------- Chrome driver initialized successfully --------------------")
driver.get("https://www.spire.umass.edu/psc/heproda/EMPLOYEE/SA/c/NUI_FRAMEWORK.PT_LANDINGPAGE.GBL")
wait = WebDriverWait(driver, 1000)

# Wait for email field
email_field = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
email_field.send_keys(os.getenv("email"), Keys.RETURN)

# Wait for password field (after page change)
password_field = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
password_field.send_keys(os.getenv("passwd"))
time.sleep(1)  # Wait for a second to ensure the password is entered correctly
sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
sign_in_button.click()

print("Waiting for the page to load...")
if "Don't ask again for 30 days" in driver.page_source:
    print("Checkbox found")
    dont_ask_30_days_chkbx = wait.until(EC.presence_of_element_located((By.ID, "idChkBx_SAOTCAS_TD")))
    dont_ask_30_days_chkbx.click()
if "Stay signed in?" not in driver.page_source:
    wait.until(EC.url_changes(driver.current_url))

stay_signed_in_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
stay_signed_in_button.click()

wait.until(EC.url_to_be("https://www.spire.umass.edu/psc/heproda/EMPLOYEE/SA/c/NUI_FRAMEWORK.PT_LANDINGPAGE.GBL"))
print("Home page loaded successfully.")
manage_classes_card = wait.until(EC.presence_of_element_located((By.ID, "win0divPTNUI_LAND_REC_GROUPLET$3")))
manage_classes_card.click()
print("Manage Classes card clicked successfully.")
add_drop_edit_classes_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "win9divSCC_LO_FL_WRK_SCC_GROUP_BOX_1$2")))
for _ in range(5):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_drop_edit_classes_dropdown)
        add_drop_edit_classes_dropdown.click()
        break
    except Exception as e:
        print(f"Error clicking Add/Drop/Edit Classes dropdown. Retrying...")
        time.sleep(0.5)
print("Add/Drop/Edit Classes dropdown clicked successfully.")

advanced_class_search_button = wait.until(EC.element_to_be_clickable((By.ID, "win9divSCC_LO_FL_WRK_SCC_GROUP_BOX_1$21$$13")))
advanced_class_search_button.click()
print("Advanced Class Search button clicked successfully.")

iframe = wait.until(EC.presence_of_element_located((By.ID, "main_target_win8")))
driver.switch_to.frame(iframe)
print("Switched to iframe: main_target_win8")

print("Waiting for the academic career dropdown to be present...")
dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_ACAD_CAREER")))
select = Select(dropdown_element)
select.select_by_visible_text("Undergraduate")
print("Academic Career set to Undergraduate successfully.")

search_open_classes_only = wait.until(EC.element_to_be_clickable((By.ID, "CLASS_SRCH_WRK2_SSR_OPEN_ONLY")))
search_open_classes_only.click()
print("Search Open Classes Only unchecked successfully.")

class_id_field = wait.until(EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_CLASS_NBR$124$")))
class_id_field.send_keys(os.getenv("class_id"), Keys.RETURN)
print("Class ID entered successfully.")

enrollment_total_element = wait.until(
    EC.presence_of_element_located((By.ID, "UM_DERIVED_SR_ENRL_TOT$0"))
)
enrollment_total = int(enrollment_total_element.text)
print(f"Enrollment total: {enrollment_total}")

enrollment_capacity_element = wait.until(
    EC.presence_of_element_located((By.ID, "UM_DERIVED_SR_ENRL_CAP$0"))
)
enrollment_capacity = int(enrollment_capacity_element.text)
print(f"Enrollment capacity: {enrollment_capacity}")

print("="*40)
print(f"Open seats: {enrollment_capacity - enrollment_total}")
print("="*40)

driver.quit()
