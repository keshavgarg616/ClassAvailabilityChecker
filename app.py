from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import smtplib, ssl
from dotenv import load_dotenv
import platform
import os
import sys

load_dotenv()

port = 465  # For SSL
context = ssl.create_default_context()

with open("course_ids.txt") as f:
    course_ids = f.readlines()
    
for i in range(len(course_ids)):
    course_ids[i] = course_ids[i].strip()

selenium_profile = os.path.join(os.getcwd(), "selenium_profile")
os.makedirs(selenium_profile, exist_ok=True)

chrome_options = Options()
try:
    if os.getenv("headless") == "true":
        chrome_options.add_argument("--headless=new")
except:
    pass
chrome_options.add_argument("--window-size=1920,1080")
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
wait = WebDriverWait(driver, 100)

# Wait for email field
email_field = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
email_field.send_keys(os.getenv("email"), Keys.RETURN)

# Wait for password field (after page change)
password_field = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
password_field.send_keys(os.getenv("passwd"))
time.sleep(1)  # Wait for a second to ensure the password is entered correctly
sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
sign_in_button.click()

time.sleep(1) 

print("Waiting for the page to load...")
if ("30 days" in driver.page_source or "Verify your identity" in driver.page_source or "Approve sign" in driver.page_source):
    print("Going through 2 factor auth")
    if os.getenv("headless") == "true":
        with open(".env", "r") as f:
            lines = f.readlines()
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("headless="):
                    f.write(f"headless=false\n")
                else:
                    f.write(line)
        print("Setting next run to headless=false for 2 factor authentication")
        driver.quit()
        sys.exit()
    print("Checkbox found")
    dont_ask_30_days_chkbx = wait.until(EC.presence_of_element_located((By.ID, "idChkBx_SAOTCAS_TD")))
    dont_ask_30_days_chkbx.click()
else: 
    print("No 2 factor authentication required")
    if os.getenv("headless") == "false":
        print("Setting next run to headless=true")
        with open(".env", "r") as f:
            lines = f.readlines()
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("headless="):
                    f.write(f"headless=true\n")
                else:
                    f.write(line)
    
if "Stay signed in?" not in driver.page_source:
    try:
        wait.until(EC.url_changes(driver.current_url))
    except:
        print("Timed out waiting for URL to change")
        if os.getenv("headless") == "true":
            with open(".env", "r") as f:
                lines = f.readlines()
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("headless="):
                        f.write(f"headless=false\n")
                    else:
                        f.write(line)
            print("Setting next run to headless=false for 2 factor authentication")
            driver.quit()
            sys.exit()

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

results = ""
open_courses = ""
full_courses = ""

for i in range(len(course_ids)):
    if i > 0:
        new_search_button = wait.until(EC.element_to_be_clickable((By.ID, "CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")))
        new_search_button.click()
    else:
        print("Waiting for the academic career dropdown to be present...")
        dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_ACAD_CAREER")))
        select = Select(dropdown_element)
        select.select_by_visible_text("Undergraduate")
        print("Academic Career set to Undergraduate successfully.")

        search_open_classes_only = wait.until(EC.element_to_be_clickable((By.ID, "CLASS_SRCH_WRK2_SSR_OPEN_ONLY")))
        search_open_classes_only.click()
        print("Search Open Classes Only unchecked successfully.")

    class_id_field = wait.until(EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_CLASS_NBR$124$")))
    class_id_field.clear()
    class_id_field.send_keys(course_ids[i], Keys.RETURN)
    print("Class ID ({}) entered successfully.".format(course_ids[i]))

    enrollment_total_element = wait.until(
        EC.presence_of_element_located((By.ID, "UM_DERIVED_SR_ENRL_TOT$0"))
    )
    enrollment_total = int(enrollment_total_element.text)
    # print(f"Enrollment total: {enrollment_total}")

    enrollment_capacity_element = wait.until(
        EC.presence_of_element_located((By.ID, "UM_DERIVED_SR_ENRL_CAP$0"))
    )
    enrollment_capacity = int(enrollment_capacity_element.text)
    # print(f"Enrollment capacity: {enrollment_capacity}")

    open_seats = enrollment_capacity - enrollment_total

    course_name = wait.until(EC.presence_of_element_located((By.ID, "DERIVED_CLSRCH_DESCR200$0"))).text
    result = f"{open_seats} open out of {enrollment_capacity} in {course_name} ({course_ids[i]})"
    results += "\nOpen seats: " + result
    if open_seats != 0:
        open_courses += result + "\n"
    else:
        full_courses += result + "\n"

print("=" * 40, end="")
print(results)
print("=" * 40)
driver.quit()

if not open_courses == "":
    print("Sending email notification...")
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(os.getenv("gmail_user"), os.getenv("gmail_password"))
        email_content = f'''Subject: Class Availability Update
        
        
Hey there!
A seat in one of the courses you're following opened up!

Open Classes:
{open_courses}
Full Classes:
{full_courses}'''
        server.sendmail(os.getenv("gmail_user"), os.getenv("email"), email_content)