import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def scrape_from_browser(route, output=None):
    # Configure the driver
    current_directory = os.getcwd()
    chrome_user_data_storage = os.path.join(current_directory, "chrome_user_data")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={chrome_user_data_storage}")
    chrome_options.add_argument("--headless")  # Enable headless mode

    # Initiate the driver and perform the scrape
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://www.bbc.com/news{route}")

    if not output:
        article_routes = []
        articles = driver.find_elements(By.XPATH, '//*[@id="topos-component"]/div[4]/div/div[1]/div/div[3]/div/div[1]')

        for article in articles:
            article_route = article.get_attribute("href")
            article_routes.append(article_route)

        driver.quit()
        return article_routes

    else:
        title_element = driver.find_element(By.CSS_SELECTOR, 'h1')
        title = title_element.text

        text_parts = driver.find_elements(By.CSS_SELECTOR, 'div[data-component="text-block"]')
        article_body = ' '.join([text_part.text for text_part in text_parts])

        article_info = {title: article_body}
        driver.quit()

        export_to_json(article_info, output)


def export_to_json(article, output):
    articles = []

    # Check if the output file exists
    if os.path.exists(f"{output}.json"):
        with open(f"{output}.json", 'r') as file:
            articles = json.load(file)

    # Check if the article already exists in the JSON
    if article not in articles:
        articles.append(article)

    # Write the JSON data to the output file
    with open(f"{output}.json", 'w') as file:
        json.dump(articles, file, indent=4)


def main():
    routes = ["/business", "/technology"]
    for route in routes:
        article_urls = scrape_from_browser(route)
        for url in article_urls:
            scrape_from_browser(url, route)


if __name__ == "__main__":
    main()
