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

# URL for Delhi District Courts cause list page
url = "https://newdelhi.dcourts.gov.in/cause-list-%e2%81%84-daily-board/"

def get_courts(driver, wait):
    # Navigate to the main page
    driver.get(url)
    time.sleep(2)  # Let page load properly
    
    # First we need to select the court complex
    complex_dropdown = wait.until(EC.presence_of_element_located((By.ID, "est_code")))
    Select(complex_dropdown).select_by_index(1)  # Select the first available complex

    # Wait for court dropdown to get populated with options
    wait.until(lambda d: len(Select(d.find_element(By.ID, "court")).options) > 1)
    court_dropdown = driver.find_element(By.ID, "court")
    select_court = Select(court_dropdown)
    
    # Extract all court options and store them
    courts = []
    for option in select_court.options[1:]:  # Skip the first empty option
        courts.append({"code": option.get_attribute("value"), "name": option.text})
    return courts

def choose_court(courts):
    # Show available courts to user
    print("Available courts:")
    court_map = {}
    for idx, court in enumerate(courts):
        print(f"{idx}: {court['name']}")
        court_map[idx] = court['code']
    
    # Keep asking until user gives valid input
    while True:
        user_input = input("Enter the court index: ").strip()
        if user_input.isdigit() and int(user_input) in court_map:
            return court_map[int(user_input)]
        print("Invalid index. Try again.")

def pick_date(driver, date_str):
    # Click on the calendar icon to open date picker
    driver.find_element(By.CSS_SELECTOR, ".icon[aria-label^='Choose Date']").click()
    time.sleep(1)
    
    # Select the specific date button
    date_btn = driver.find_element(By.CSS_SELECTOR, f"button.dateButton[data-date='{date_str}']")
    date_btn.click()
    time.sleep(1)

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
    # Setup PDF document
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

    # Set column widths - these work well for court data
    COL_W0 = 35                   # Serial number doesn't need much space
    COL_W1 = 115                  # Case numbers are medium length
    COL_W2 = 250                  # Party names can be really long
    COL_W3 = PAGE_WIDTH - (COL_W0 + COL_W1 + COL_W2)  # Whatever space left for advocate

    for caption, headers, rows in all_tables:
        # Fix the header text - website uses "Serial Number" but "Sr. No." looks better
        if headers and headers[0].lower().startswith("serial"):
            headers[0] = "Sr. No."

        # Add table title
        elements.append(Paragraph(f"<b>{caption}</b>", heading))
        elements.append(Spacer(1, 6))

        # Create table with proper text wrapping
        header_paragraphs = [Paragraph(f"<b>{h}</b>", normal) for h in headers]
        data = [header_paragraphs]

        # Add each row as paragraphs so text can wrap
        for row in rows:
            data.append([Paragraph(str(cell), normal) for cell in row])

        table = Table(
            data,
            colWidths=[COL_W0, COL_W1, COL_W2, COL_W3],
            repeatRows=1  # Repeat headers on new pages
        )

        # Make the table look professional
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),

            # Add some padding so text doesn't stick to borders
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

            # Borders and alternating row colors for readability
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))  # Space between tables

    doc.build(elements)

def main():
    # Setup Chrome browser
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        # Get list of all courts
        courts = get_courts(driver, wait)
        
        # Show courts and let user pick one
        print("Available courts:")
        for idx, court in enumerate(courts):
            print(f"{idx}: {court['name']}")
        
        # Keep asking for valid court selection
        court_idx = None
        while True:
            user_input = input("Enter the court index: ").strip()
            if user_input.isdigit() and int(user_input) in range(len(courts)):
                court_idx = int(user_input)
                break
            print("Invalid index. Try again.")
        
        # Get the selected court details
        court_code = courts[court_idx]['code']
        judge_name = courts[court_idx]['name'].replace('/', '_').replace('\\', '_').replace(' ', '_')
        
        # Select the court in dropdown
        Select(driver.find_element(By.ID, "court")).select_by_value(court_code)
        time.sleep(1)
        
        # Get date from user and set it
        date_str = input("Enter cause list date (YYYY-MM-DD): ").strip()
        pick_date(driver, date_str)
        
        # Set case type
        pick_case_type(driver)
        
        # User needs to solve captcha manually
        print("\nSolve the CAPTCHA in the browser if prompted.")
        input("Press ENTER after solving CAPTCHA to continue...")
        
        # Submit the search
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Search']").click()
        
        try:
            # Wait for results to load
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".distTableContent")))
            time.sleep(2)  # Give it a bit more time to fully load
            
            # Find all result tables
            dist_contents = driver.find_elements(By.CSS_SELECTOR, ".distTableContent")
            all_tables = []
            
            for content in dist_contents:
                tables = content.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    # Get table title
                    caption_elems = table.find_elements(By.TAG_NAME, "caption")
                    caption = caption_elems[0].text if caption_elems else "Cause List"
                    
                    # Get column headers
                    headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
                    
                    # Extract all rows
                    rows = []
                    for row in table.find_elements(By.TAG_NAME, "tr")[1:]:  # Skip header row
                        cells = []
                        for td in row.find_elements(By.TAG_NAME, "td"):
                            # Some cells have content in spans with bt-content class
                            bt_content = td.find_elements(By.CLASS_NAME, "bt-content")
                            if bt_content:
                                cells.append(bt_content[0].text)
                            else:
                                cells.append(td.text)
                        if cells:  # Only add non-empty rows
                            rows.append(cells)
                    
                    # Show results in console
                    print(f"\n=== {caption} ===")
                    if headers:
                        print(" | ".join(headers))
                    for row in rows:
                        print(" | ".join(row))
                    
                    all_tables.append((caption, headers, rows))
            
            # Save everything to PDF if we found data
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