import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_from_browser(route, output=None):
    # Configure the driver
    current_directory = os.getcwd()
    chrome_user_data_storage = os.path.join(current_directory, "chrome_user_data")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={chrome_user_data_storage}")
    # chrome_options.add_argument("--headless")  # Enable headless mode

    # Initiate the driver and perform the scrape
    driver = webdriver.Chrome(options=chrome_options)
    
    print(route)

    time.sleep(3)  # Wait for 3 seconds to allow the page to load

    if not output:
        driver.get(f"https://www.bbc.com/{route[1:]}")
        article_routes = []
        articles = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="topos-component"]//a[@href]')
            )
        )

        for article in articles:
            article_route = article.get_attribute("href")
            article_routes.append(article_route)

        driver.quit()
        return article_routes

    else:
        driver.get(route)
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h1')
            )
        )
        title = title_element.text

        try:
            text_parts = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'div[data-component="text-block"]')
                )
            )
            article_body = ' '.join([text_part.text for text_part in text_parts])
        except:
            article_body = ""

        article_info = {title: article_body}
        driver.quit()

        if article_body:
            export_to_json(article_info, output[1:])
        else:
            print("Article content not found. Skipping the URL.")

        return []  # Return an empty list when output is provided


def export_to_json(article, output):
    print(output)
    output_path = f"{output}.json"

    if not os.path.exists(output_path):
        # File doesn't exist, create it
        with open(output_path, 'w') as file:
            json.dump([], file)  # Initialize with an empty JSON array
        print("Output file created:", output_path)

    # Load existing articles from the file
    with open(output_path, 'r') as file:
        articles = json.load(file)

    # Check if the article already exists in the JSON
    if article not in articles:
        articles.append(article)
        print("Article added to JSON:", article)

    # Write the updated JSON data to the file
    with open(output_path, 'w') as file:
        json.dump(articles, file, indent=4)
        print("Data written to output file:", output_path)

    print("Export process completed.")


def main():
    routes = ["/business", "/technology"]
    for route in routes:
        article_urls = scrape_from_browser(route)
        for url in article_urls:
            print(url)
            article_urls += scrape_from_browser(url, route)


if __name__ == "__main__":
    main()
