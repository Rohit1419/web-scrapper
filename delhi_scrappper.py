from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

url = "https://newdelhi.dcourts.gov.in/cause-list-%e2%81%84-daily-board/"

def get_courts(driver, wait):
    driver.get(url)
    time.sleep(2)
    complex_dropdown = wait.until(EC.presence_of_element_located((By.ID, "est_code")))
    Select(complex_dropdown).select_by_index(1)

    wait.until(lambda d: len(Select(d.find_element(By.ID, "court")).options) > 1)
    court_dropdown = driver.find_element(By.ID, "court")
    select_court = Select(court_dropdown)
    courts = []
    for option in select_court.options[1:]:
        courts.append({"code": option.get_attribute("value"), "name": option.text})
    return courts

def choose_court(courts):
    print("Available courts:")
    court_map = {}
    for idx, court in enumerate(courts):
        print(f"{idx}: {court['name']}")
        court_map[idx] = court['code']
    while True:
        user_input = input("Enter the court index: ").strip()
        if user_input.isdigit() and int(user_input) in court_map:
            return court_map[int(user_input)]
        print("Invalid index. Try again.")

def pick_date(driver):
    date_str = input("Enter cause list date (YYYY-MM-DD): ").strip()
    driver.find_element(By.CSS_SELECTOR, ".icon[aria-label^='Choose Date']").click()
    time.sleep(1)
    date_btn = driver.find_element(By.CSS_SELECTOR, f"button.dateButton[data-date='{date_str}']")
    date_btn.click()
    time.sleep(1)

def pick_case_type(driver):
    case_type = input("Enter case type (civil/criminal, default civil): ").strip().lower()
    if case_type == "criminal":
        driver.find_element(By.ID, "chkCauseTypeCriminal").click()
    else:
        driver.find_element(By.ID, "chkCauseTypeCivil").click()
    time.sleep(1)

def main():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        courts = get_courts(driver, wait)
        court_code = choose_court(courts)
        Select(driver.find_element(By.ID, "court")).select_by_value(court_code)
        time.sleep(1)
        pick_date(driver)
        pick_case_type(driver)
        print("\nSolve the CAPTCHA in the browser if prompted.")
        input("Press ENTER after solving CAPTCHA to continue...")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Search']").click()
        # Waiting for  for tables to appear
        try:
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".distTableContent")))
            time.sleep(2)  

            dist_contents = driver.find_elements(By.CSS_SELECTOR, ".distTableContent")
            found_table = False
            for content in dist_contents:
                tables = content.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    found_table = True
                    caption_elems = table.find_elements(By.TAG_NAME, "caption")
                    caption = caption_elems[0].text if caption_elems else "Cause List"
                    print(f"\n=== {caption} ===")
                    headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
                    if headers:
                        print(" | ".join(headers))
                    for row in table.find_elements(By.TAG_NAME, "tr")[1:]:
                        cells = []
                        for td in row.find_elements(By.TAG_NAME, "td"):
                            bt_content = td.find_elements(By.CLASS_NAME, "bt-content")
                            if bt_content:
                                cells.append(bt_content[0].text)
                            else:
                                cells.append(td.text)
                        if cells:
                            print(" | ".join(cells))
            if not found_table:
                print("No tables found in .distTableContent. Printing raw HTML for debugging:")
                for content in dist_contents:
                    print(content.get_attribute("outerHTML"))
        except Exception as e:
            print("Error fetching cause list:", e)

        input("\nPress ENTER to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()