import requests
import time

BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Get available courts
    print("Getting courts...")
    response = requests.get(f"{BASE_URL}/api/courts")
    courts = response.json()
    print(f"Found {len(courts)} courts")
    
    # 2. Start scraping
    scrape_request = {
        "court_index": 8,  # Adjust based on available courts
        "date": "2025-10-16",
        "case_type": "civil"
    }
    
    print("Starting scrape...")
    response = requests.post(f"{BASE_URL}/api/scrape/start", json=scrape_request)
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"Session ID: {session_id}")
    
    # 3. Check status
    while True:
        response = requests.get(f"{BASE_URL}/api/scrape/status/{session_id}")
        status = response.json()
        print(f"Status: {status['status']} - {status['message']}")
        
        if status["status"] == "captcha_required":
            input("Solve CAPTCHA in browser, then press ENTER...")
            requests.post(f"{BASE_URL}/api/scrape/captcha-solved/{session_id}")
        
        if status["status"] in ["completed", "error"]:
            break
        
        time.sleep(3)
    
    print("Done!")

if __name__ == "__main__":
    test_api()