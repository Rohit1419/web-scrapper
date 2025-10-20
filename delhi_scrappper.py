from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
import time

url = "https://newdelhi.dcourts.gov.in/cause-list-%e2%81%84-daily-board/"

# selcting 1st court complex 
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

# choosing the court by user input
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

def pick_date(driver, date_str):
   
    driver.find_element(By.CSS_SELECTOR, ".icon[aria-label^='Choose Date']").click()
    time.sleep(1)
    
    
    date_btn = driver.find_element(By.CSS_SELECTOR, f"button.dateButton[data-date='{date_str}']")
    date_btn.click()
    time.sleep(1)

# selecting case type 
def pick_case_type(driver):
    # Ask user what type of cases they want
    case_type = input("Enter case type (civil/criminal, default civil): ").strip().lower()
    
    if case_type == "criminal":
        driver.find_element(By.ID, "chkCauseTypeCriminal").click()
    else:
        # Default to civil cases
        driver.find_element(By.ID, "chkCauseTypeCivil").click()
    time.sleep(1)

def save_all_tables_to_pdf(all_tables, filename):
   
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = styles['Heading3']

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30
    )

    elements = []
    PAGE_WIDTH = doc.width

    
    COL_W0 = 35                   # Serial number
    COL_W1 = 115                  # Case numbers a
    COL_W2 = 250                  # Party names 
    COL_W3 = PAGE_WIDTH - (COL_W0 + COL_W1 + COL_W2)  

    for caption, headers, rows in all_tables:
       
        if headers and headers[0].lower().startswith("serial"):
            headers[0] = "Sr. No."

        
        elements.append(Paragraph(f"<b>{caption}</b>", heading))
        elements.append(Spacer(1, 6))

        
        header_paragraphs = [Paragraph(f"<b>{h}</b>", normal) for h in headers]
        data = [header_paragraphs]

        
        for row in rows:
            data.append([Paragraph(str(cell), normal) for cell in row])

        table = Table(
            data,
            colWidths=[COL_W0, COL_W1, COL_W2, COL_W3],
            repeatRows=1  
        )

        
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),

            
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))  

    doc.build(elements)

def main():
   
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        
        courts = get_courts(driver, wait)
        
        
        print("Available courts:")
        for idx, court in enumerate(courts):
            print(f"{idx}: {court['name']}")
        
       
        court_idx = None
        while True:
            print("Some of the courts and date variation may not have records, try this one : court index = 8 ; date = 2025-10-16 ; case type = civil")
            user_input = input("Enter the court index: ").strip()
            if user_input.isdigit() and int(user_input) in range(len(courts)):
                court_idx = int(user_input)
                break
            print("Invalid index. Try again.")
        
       
        court_code = courts[court_idx]['code']
        judge_name = courts[court_idx]['name'].replace('/', '_').replace('\\', '_').replace(' ', '_')
        
       
        Select(driver.find_element(By.ID, "court")).select_by_value(court_code)
        time.sleep(1)
        
        
        date_str = input("Enter cause list date (YYYY-MM-DD): ").strip()
        pick_date(driver, date_str)
        
        
        pick_case_type(driver)
        
        
        print("\nSolve the CAPTCHA in the browser if prompted.")
        input("Press ENTER after solving CAPTCHA to continue...")
        
        
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Search']").click()
        
        try:
          
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".distTableContent")))
            time.sleep(2)

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
                    
                    
                    print(f"\n=== {caption} ===")
                    if headers:
                        print(" | ".join(headers))
                    for row in rows:
                        print(" | ".join(row))
                    
                    all_tables.append((caption, headers, rows))
            
           
            if all_tables:
                downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
                os.makedirs(downloads_dir, exist_ok=True)
                pdf_filename = os.path.join(
                    downloads_dir,
                    f"cause_list_{judge_name}_{date_str}.pdf"
                )
                save_all_tables_to_pdf(all_tables, pdf_filename)
                print(f"Saved all cause lists to {pdf_filename}")
            else:
                print("No tables found in .distTableContent.")
                
        except Exception as e:
            print("Error fetching cause list:", e)
            
        input("\nPress ENTER to close browser...")
        
    finally:
        # Always close the browser
        driver.quit()

if __name__ == "__main__":
    main()