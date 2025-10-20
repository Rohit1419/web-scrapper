from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from captcha_solver import auto_solve_captcha
import time


CAPTCHA_API_KEY = "my-api-key-here" # Replace with your actual key if u want to try. get it from 2Captcha.com

url = "https://newdelhi.dcourts.gov.in/cause-list-%e2%81%84-daily-board/"

def get_courts(driver, wait):
    """Get all available courts - same logic as your main scraper"""
    complex_dropdown = wait.until(EC.presence_of_element_located((By.ID, "est_code")))
    
    # Get all complex options
    complex_options = Select(complex_dropdown).options[1:]  # Skip first empty option
    courts = []
    
    for i, complex_option in enumerate(complex_options):
        Select(complex_dropdown).select_by_index(i + 1)
        time.sleep(1)
        
        # Wait for court dropdown to populate
        wait.until(lambda d: len(Select(d.find_element(By.ID, "court")).options) > 1)
        
        court_dropdown = driver.find_element(By.ID, "court")
        court_options = Select(court_dropdown).options[1:]  # Skip first empty option
        
        for court_option in court_options:
            courts.append({
                'name': court_option.text,
                'code': court_option.get_attribute('value')
            })
    
    return courts

def test_captcha_solver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        print("Navigating to court website...")
        driver.get(url)
        time.sleep(3)
        
        print("Getting all courts...")
        courts = get_courts(driver, wait)
        
        print(f"Found {len(courts)} courts total")
        
        if len(courts) <= 8:
            print(f"❌ Error: Only {len(courts)} courts found, but you requested index 8")
            for i, court in enumerate(courts):
                print(f"  {i}: {court['name']}")
            return
        
        # Select court at index 8
        selected_court = courts[8]
        print(f"Selected court (index 8): {selected_court['name']}")
        
        # Select the court
        court_dropdown = driver.find_element(By.ID, "court")
        Select(court_dropdown).select_by_value(selected_court['code'])
        time.sleep(1)
        
        print("Setting date to 2025-10-16...")
        driver.find_element(By.CSS_SELECTOR, ".icon[aria-label^='Choose Date']").click()
        time.sleep(1)
        
        # Set the specific date
        try:
            date_btn = driver.find_element(By.CSS_SELECTOR, "button.dateButton[data-date='2025-10-16']")
            date_btn.click()
            time.sleep(1)
            print("✅ Date set to 2025-10-16")
        except:
            print("❌ Date 2025-10-16 not available, using today's date")
            # Fallback to available date
            available_dates = driver.find_elements(By.CSS_SELECTOR, "button.dateButton")
            if available_dates:
                available_dates[0].click()
                time.sleep(1)
        
        print("Setting case type to Civil...")
        driver.find_element(By.ID, "chkCauseTypeCivil").click()
        time.sleep(1)
        
        print("Submitting search - CAPTCHA should appear...")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Search']")
        submit_btn.click()
        time.sleep(3)
        
        print("Attempting to solve CAPTCHA automatically...")
        if auto_solve_captcha(driver, CAPTCHA_API_KEY):
            print("✅ CAPTCHA solved automatically!")
            
            print("Submitting form after CAPTCHA solution...")
            submit_btn.click()
            time.sleep(5)
            
            # Check for results and extract data
            try:
                results = driver.find_elements(By.CSS_SELECTOR, ".distTableContent")
                if results:
                    print(f"✅ SUCCESS! Found {len(results)} result sections")
                    
                    # Extract table data like your main scraper
                    for i, content in enumerate(results):
                        print(f"\n--- Result Section {i+1} ---")
                        tables = content.find_elements(By.TAG_NAME, "table")
                        
                        for j, table in enumerate(tables):
                            # Get caption
                            caption_elems = table.find_elements(By.TAG_NAME, "caption")
                            caption = caption_elems[0].text if caption_elems else f"Table {j+1}"
                            print(f"Table: {caption}")
                            
                            # Get headers
                            headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
                            print(f"Headers: {headers}")
                            
                            # Get first few rows
                            rows = table.find_elements(By.TAG_NAME, "tr")[1:6]  # First 5 data rows
                            for k, row in enumerate(rows):
                                cells = []
                                for td in row.find_elements(By.TAG_NAME, "td"):
                                    bt_content = td.find_elements(By.CLASS_NAME, "bt-content")
                                    if bt_content:
                                        cells.append(bt_content[0].text)
                                    else:
                                        cells.append(td.text)
                                
                                if cells:
                                    print(f"  Row {k+1}: {cells}")
                            
                            total_rows = len(table.find_elements(By.TAG_NAME, "tr")) - 1  # Minus header
                            print(f"  Total rows in this table: {total_rows}")
                            print()
                
                else:
                    print("❌ No results found")
                    # Check if there's an error message
                    error_msgs = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, [class*='error']")
                    if error_msgs:
                        print("Error message:", error_msgs[0].text)
                    
            except Exception as e:
                print(f"❌ Error extracting results: {e}")
        else:
            print("❌ Auto-solve failed")
            print("The page is still open - you can solve manually to see results...")
        
        input("Press ENTER to close browser...")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing CAPTCHA auto-solver for:")
    print("- Court index: 8")
    print("- Date: 2025-10-16")
    print("- Case type: Civil")
    print()
    test_captcha_solver()