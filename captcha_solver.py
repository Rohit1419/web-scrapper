import requests
import base64
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TwoCaptchaSolver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
    
    def solve_image_captcha(self, driver):
        try:
            print("Looking for CAPTCHA image...")
            
            # Wait for CAPTCHA image to load
            captcha_img = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='captcha'], img[src*='Captcha'], img[alt*='captcha'], img[alt*='Captcha']"))
            )
            
            print("CAPTCHA image found, capturing...")
            
            # Get image as base64
            img_base64 = driver.execute_script("""
                var canvas = document.createElement('canvas');
                var ctx = canvas.getContext('2d');
                var img = arguments[0];
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                return canvas.toDataURL('image/png').substring(22);
            """, captcha_img)
            
            print("Submitting CAPTCHA to 2captcha service...")
            
            # Submit to 2captcha
            submit_data = {
                "key": self.api_key,
                "method": "base64",
                "body": img_base64
            }
            
            response = requests.post(f"{self.base_url}/in.php", data=submit_data, timeout=30)
            print(f"Submit response: {response.text}")
            
            if "OK|" in response.text:
                captcha_id = response.text.split("|")[1]
                print(f"CAPTCHA submitted with ID: {captcha_id}")
                
                # Wait for solution
                print("Waiting for CAPTCHA solution...")
                for attempt in range(60):  # Wait up to 10 minutes
                    time.sleep(10)
                    
                    result_params = {
                        "key": self.api_key,
                        "action": "get",
                        "id": captcha_id
                    }
                    
                    result = requests.get(f"{self.base_url}/res.php", params=result_params, timeout=30)
                    print(f"Attempt {attempt + 1}: {result.text}")
                    
                    if "OK|" in result.text:
                        solution = result.text.split("|")[1]
                        print(f"CAPTCHA solved! Solution: {solution}")
                        return solution
                    elif "CAPCHA_NOT_READY" not in result.text:
                        print(f"Error getting solution: {result.text}")
                        break
                
                print("Timeout waiting for CAPTCHA solution")
                return None
            else:
                print(f"Error submitting CAPTCHA: {response.text}")
                return None
                
        except Exception as e:
            print(f"CAPTCHA solving error: {e}")
            return None
    
    def enter_captcha_solution(self, driver, solution):
        try:
            # Find CAPTCHA input field - try common selectors
            captcha_selectors = [
                "input[name*='captcha']",
                "input[id*='captcha']",
                "input[placeholder*='captcha']",
                "input[type='text'][name*='code']",
                "#captcha",
                ".captcha-input"
            ]
            
            captcha_input = None
            for selector in captcha_selectors:
                try:
                    captcha_input = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not captcha_input:
                print("Could not find CAPTCHA input field")
                return False
            
            print(f"Entering solution: {solution}")
            captcha_input.clear()
            captcha_input.send_keys(solution)
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Error entering CAPTCHA solution: {e}")
            return False

def auto_solve_captcha(driver, api_key):
    if not api_key or api_key == "YOUR_2CAPTCHA_API_KEY":
        print("No valid 2captcha API key provided")
        return False
    
    solver = TwoCaptchaSolver(api_key)
    
    try:
        solution = solver.solve_image_captcha(driver)
        if solution:
            return solver.enter_captcha_solution(driver, solution)
        else:
            return False
    except Exception as e:
        print(f"Auto solve CAPTCHA failed: {e}")
        return False