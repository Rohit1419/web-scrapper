from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

def fetch_states():

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options = options)
    wait  = WebDriverWait(driver, 10)

    try:
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
         
        driver.get(url)
        time.sleep(2)

        state_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "sess_state_code"))
        
        )

        select = Select(state_dropdown)

        states = []
        for option in select.options[1:]:
             states.append({"code": option.get_attribute("value"), "name": option.text})

        print ("available states:")
        
        for state in states:
            print(f"  - {state['name']} ({state['code']})")

        return states
    
    
    finally:
        driver.quit()
         


if __name__ == "__main__":
    fetch_states()#