from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

def scrape_trustpilot_reviews(company_url, output_file, max_reviews=50):
    # Setup Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (remove for debugging)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    service = Service("/Users/wangyixun/.wdm/drivers/chromedriver/mac64/131.0.6778.108/chromedriver-mac-x64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    reviews_data = []
    total_valid_reviews = 0  # To count valid reviews
    page = 1

    try:
        while total_valid_reviews < max_reviews:
            url = f"{company_url}?page={page}"
            driver.get(url)

            # Wait for reviews to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.styles_cardWrapper__LcCPA"))
            )

            # Locate all review blocks
            reviews = driver.find_elements(By.CSS_SELECTOR, "div.styles_cardWrapper__LcCPA")
            print(f"Found {len(reviews)} reviews on page {page}")

            if not reviews:
                print("No more reviews found.")
                break

            for review in reviews:
                if total_valid_reviews >= max_reviews:
                    break

                # Extract Review Title
                try:
                    review_title = review.find_element(By.CSS_SELECTOR, "h2.typography_heading-s__f7029").text.strip()
                except Exception:
                    review_title = "N/A"

                # Extract Review Text
                try:
                    review_text = review.find_element(By.CSS_SELECTOR, "p.typography_body-l__KUYFJ").text.strip()
                except Exception:
                    review_text = "N/A"

                # Extract Star Rating
                try:
                    star_rating = review.find_element(By.CSS_SELECTOR, "img[src*='stars']").get_attribute("alt").split(" ")[1]
                except Exception:
                    star_rating = "N/A"

                # Extract Date of Experience
                try:
                    date_text = review.find_element(By.CSS_SELECTOR, "p.typography_body-m__xgxZ_").text.strip()
                    raw_date = date_text.split(":")[-1].strip()
                    date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
                except Exception:
                    date = "N/A"

                # Extract Author Name
                try:
                    author = review.find_element(By.CSS_SELECTOR, "span[data-consumer-name-typography='true']").text.strip()
                except Exception:
                    author = "N/A"

                # Extract Location
                try:
                    location = review.find_element(By.CSS_SELECTOR, "div[data-consumer-country-typography='true'] span").text.strip()
                except Exception:
                    location = "N/A"

                # Append only valid reviews (review_text must not be N/A)
                if review_text != "N/A":
                    reviews_data.append([total_valid_reviews + 1, review_title, review_text, star_rating, date, author, location])
                    total_valid_reviews += 1
                else:
                    print("Invalid review (N/A), skipping...")

            #print(f"Page {page} scraped.")
            page += 1

    finally:
        driver.quit()

    # Save reviews to a CSV file
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["No.", "Review Title", "Review Text", "Star Rating", "Date", "Author", "Location"])
        writer.writerows(reviews_data)

    print(f"Reviews saved to {output_file}")

# Configures:
company_url = "https://www.trustpilot.com/review/www.mountainroseherbs.com"
output_file = "mountainroseherbs.csv"
scrape_trustpilot_reviews(company_url, output_file, max_reviews=500)
