from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"


def fetch_states(driver, wait):
    driver.get(url)
    time.sleep(2)
    state_dropdown = wait.until(
        EC.presence_of_element_located((By.ID, "sess_state_code"))
    )
    select = Select(state_dropdown)
    states = []
    for option in select.options[1:]:
        states.append({"code": option.get_attribute("value"), "name": option.text})
    return states

def fetch_districts(driver, wait, state_code):
    # Select the state
    state_dropdown = Select(driver.find_element(By.ID, "sess_state_code"))
    state_dropdown.select_by_value(state_code)
    time.sleep(2)  # Wait for districts to load

    district_dropdown = wait.until(
        EC.presence_of_element_located((By.ID, "sess_dist_code"))
    )
    select = Select(district_dropdown)
    districts = []
    for option in select.options[1:]:
        districts.append({"code": option.get_attribute("value"), "name": option.text})
    
    return districts

def fetch_court_complexes(driver, wait, district_code):
    # Select the district
    district_dropdown = Select(driver.find_element(By.ID, "sess_dist_code"))
    district_dropdown.select_by_value(district_code)
    time.sleep(2)  # Wait for complexes to load

    complex_dropdown = wait.until(
        EC.presence_of_element_located((By.ID, "court_complex_code"))
    )
    select = Select(complex_dropdown)
    complexes = []
    for option in select.options[1:]:
        complexes.append({"code": option.get_attribute("value"), "name": option.text})
    return complexes

def fetch_court_names(driver, wait, complex_code):
    # Select the court complex
    complex_dropdown = Select(driver.find_element(By.ID, "court_complex_code"))
    complex_dropdown.select_by_value(complex_code)
    
    # Wait for the court names dropdown to be present and have options
    try:
        wait.until(lambda d: len(Select(d.find_element(By.ID, "CL_court_no")).options) > 1)
        court_dropdown = driver.find_element(By.ID, "CL_court_no")
    except Exception as e:
        print("Could not find court dropdown:", e)
        print(driver.page_source[:1000])  # For debugging
        return []

    select = Select(court_dropdown)
    courts = []
    for option in select.options[1:]:
        courts.append({"code": option.get_attribute("value"), "name": option.text})
    return courts

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        states = fetch_states(driver, wait)
        
        # print the states 

        print("Available states:")
        for state in states:
            print(f"  - {state['name']} ({state['code']})")
        state_code = input("Enter the state code to fetch districts: ").strip()
        districts = fetch_districts(driver, wait, state_code)

        #print the districts in the states
        print(f"Districts in selected state ({state_code}):")
        for district in districts:
            print(f"  - {district['name']} ({district['code']})")
        
        district_code = input("Enter the district code to fetch court complexes: ").strip()
        complexes = fetch_court_complexes(driver, wait, district_code)

        #print the court complexes in the districts
        print(f"Court Complexes in district ({district_code}):")
        for comp in complexes:
            print(f"  - {comp['name']} ({comp['code']})")
        
        complex_code = input("Enter the court complex code to fetch court names: ").strip()
        courts = fetch_court_names(driver, wait, complex_code)

        #print the court names in the complexes
        
        print(f"Courts in complex ({complex_code}):")
        for court in courts:
            print(f"  - {court['name']} ({court['code']})")

         # Select court
        court_code = input("Enter the court code to fetch cause list: ").strip()
        # Select the court name
        court_dropdown = Select(driver.find_element(By.ID, "CL_court_no"))
        court_dropdown.select_by_value(court_code)
        time.sleep(1)

        # Enter cause list date
        date_str = input("Enter cause list date (DD-MM-YYYY): ").strip()
        date_input = driver.find_element(By.ID, "causelist_date")
        date_input.clear()
        date_input.send_keys(date_str)
        time.sleep(1)

        # Pause for CAPTCHA
        print("\nIf CAPTCHA is shown in browser, please solve it manually.")
        input("Press ENTER after solving CAPTCHA to continue...")

        # Submit the form for Civil or Criminal cause list
        case_type = input("Enter case type (civil/criminal): ").strip().lower()
        if case_type == "civil":
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Civil')]")
        else:
            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Criminal')]")
        submit_btn.click()
        time.sleep(3)

        # Look for PDF download link
        try:
            pdf_link = driver.find_element(By.LINK_TEXT, "Download Cause List")
            pdf_url = pdf_link.get_attribute("href")
            print(f"PDF available at: {pdf_url}")
            pdf_link.click()
            print("PDF download initiated (check your browser's download folder).")
        except Exception as e:
            print("No PDF download link found or error occurred:", e)
        
    finally:
        driver.quit()