from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import threading
import uuid
import os
from datetime import datetime

#  scraper functions
from delhi_scrappper import get_courts, save_all_tables_to_pdf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

app = FastAPI(title="ecourt-scraper")

#  CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active scraping sessions
active_sessions = {}

class Court(BaseModel):
    index: int
    name: str
    code: str

class ScrapeRequest(BaseModel):
    court_index: int
    date: str  # YYYY-MM-DD format
    case_type: str  # "civil" or "criminal"

class ScrapeResponse(BaseModel):
    session_id: str
    status: str
    message: str
    captcha_needed: Optional[bool] = False

class SessionStatus(BaseModel):
    session_id: str
    status: str  # "pending", "captcha_required", "processing", "completed", "error"
    message: str
    pdf_url: Optional[str] = None
    tables: Optional[List] = None

@app.get("/")
def root():
    return {"message": "ecourt-scraper is running!"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/courts", response_model=List[Court])
async def get_available_courts():
    """Get list of available courts"""
    try:
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)
        
        try:
            courts = get_courts(driver, wait)
            court_list = []
            for idx, court in enumerate(courts):
                court_list.append(Court(
                    index=idx,
                    name=court['name'],
                    code=court['code']
                ))
            return court_list
        finally:
            driver.quit()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching courts: {str(e)}")

@app.post("/api/scrape/start", response_model=ScrapeResponse)
async def start_scraping(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Start the scraping process"""
    session_id = str(uuid.uuid4())
    
    # Store session info
    active_sessions[session_id] = {
        "status": "pending",
        "message": "Initializing scraper...",
        "court_index": request.court_index,
        "date": request.date,
        "case_type": request.case_type,
        "driver": None,
        "pdf_url": None
    }
    
    
    background_tasks.add_task(run_scraper, session_id, request)
    
    return ScrapeResponse(
        session_id=session_id,
        status="pending",
        message="Scraper started. Please check status for updates."
    )

@app.get("/api/scrape/status/{session_id}", response_model=SessionStatus)
async def get_scrape_status(session_id: str):
    """Get status of scraping session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return SessionStatus(
        session_id=session_id,
        status=session["status"],
        message=session["message"],
        pdf_url=session.get("pdf_url"),
        tables=session.get("tables")
    )

@app.post("/api/scrape/captcha-solved/{session_id}")
async def captcha_solved(session_id: str):
    """Notify that CAPTCHA has been solved"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    if session["status"] != "captcha_required":
        raise HTTPException(status_code=400, detail="Session not waiting for CAPTCHA")
    
    session["captcha_solved"] = True
    return {"message": "CAPTCHA confirmation received"}

@app.delete("/api/scrape/{session_id}")
async def cancel_scraping(session_id: str):
    """Cancel scraping session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    if session.get("driver"):
        session["driver"].quit()
    
    del active_sessions[session_id]
    return {"message": "Session cancelled"}

async def run_scraper(session_id: str, request: ScrapeRequest):
    """Background task to run the scraper"""
    session = active_sessions[session_id]
    
    try:
        
        session["status"] = "initializing"
        session["message"] = "Setting up browser..."
        
        options = webdriver.ChromeOptions()
        
        options.add_argument("--start-maximized")
        
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)
        session["driver"] = driver
        
        
        session["message"] = "Loading courts..."
        courts = get_courts(driver, wait)
        
        if request.court_index >= len(courts):
            raise Exception("Invalid court index")
        
        selected_court = courts[request.court_index]
        
       
        session["message"] = "Selecting court..."
        Select(driver.find_element(By.ID, "court")).select_by_value(selected_court['code'])
        time.sleep(1)
        
        
        session["message"] = "Setting date..."
        driver.find_element(By.CSS_SELECTOR, ".icon[aria-label^='Choose Date']").click()
        time.sleep(1)
        date_btn = driver.find_element(By.CSS_SELECTOR, f"button.dateButton[data-date='{request.date}']")
        date_btn.click()
        time.sleep(1)
        
        
        session["message"] = "Setting case type..."
        if request.case_type.lower() == "criminal":
            driver.find_element(By.ID, "chkCauseTypeCriminal").click()
        else:
            driver.find_element(By.ID, "chkCauseTypeCivil").click()
        time.sleep(1)
        
        
        session["status"] = "captcha_required"
        session["message"] = "Please solve CAPTCHA in the browser window"
        session["captcha_solved"] = False
        
        
        timeout = 300  
        elapsed = 0
        while not session.get("captcha_solved", False) and elapsed < timeout:
            await asyncio.sleep(2)
            elapsed += 2
        
        if not session.get("captcha_solved", False):
            raise Exception("CAPTCHA timeout - please try again")
        
        
        session["status"] = "processing"
        session["message"] = "Searching for cause list..."
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Search']").click()
        
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".distTableContent")))
        time.sleep(2)
        
        
        session["message"] = "Extracting cause list data..."
        dist_contents = driver.find_elements(By.CSS_SELECTOR, ".distTableContent")
        all_tables = []
        
        for content in dist_contents:
            tables = content.find_elements(By.TAG_NAME, "table")
            for table in tables:
                caption_elems = table.find_elements(By.TAG_NAME, "caption")
                caption = caption_elems[0].text if caption_elems else "Cause List"
                
                headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
                
                rows = []
                for row in table.find_elements(By.TAG_NAME, "tr")[1:]:
                    cells = []
                    for td in row.find_elements(By.TAG_NAME, "td"):
                        bt_content = td.find_elements(By.CLASS_NAME, "bt-content")
                        if bt_content:
                            cells.append(bt_content[0].text)
                        else:
                            cells.append(td.text)
                    if cells:
                        rows.append(cells)
                
                all_tables.append((caption, headers, rows))
        
        # Generate PDF
        if all_tables:
            session["message"] = "Generating PDF..."
            downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            judge_name = selected_court['name'].replace('/', '_').replace('\\', '_').replace(' ', '_')
            pdf_filename = f"cause_list_{judge_name}_{request.date}.pdf"
            pdf_path = os.path.join(downloads_dir, pdf_filename)
            
            save_all_tables_to_pdf(all_tables, pdf_path)
            
            session["status"] = "completed"
            session["message"] = "Cause list extracted successfully!"
            session["pdf_url"] = f"/downloads/{pdf_filename}"
            session["tables"] = [{"caption": cap, "headers": headers, "rows": rows} 
                              for cap, headers, rows in all_tables]
        else:
            session["status"] = "completed"
            session["message"] = "No cause list found for the selected parameters"
        
    except Exception as e:
        session["status"] = "error"
        session["message"] = f"Error: {str(e)}"
    
    finally:
        if session.get("driver"):
            session["driver"].quit()

# Serve PDF files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """Download generated PDF files"""
    file_path = os.path.join("downloads", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

def main():
    print("Hello from ecourt-scraper!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)