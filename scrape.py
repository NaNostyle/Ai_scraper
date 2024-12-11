from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

AUTH = 'brd-customer-hl_f2e06bf4-zone-scraping_browser1:k4ef5dpjnsv0'
SBR_WS_CDP = f'https://{AUTH}@brd.superproxy.io:9222'


def scrape_website(website):
    print("Launching Playwright Browser...")
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(SBR_WS_CDP)
        page = browser.new_page()

        # Navigate to the website
        print(f"Navigating to {website}...")
        page.goto(website, timeout=60000)  # 60 seconds

        # Handle cookie consent pop-up
        print("Looking for 'Accepter & Fermer' button...")
        try:
            page.locator("text='Accepter & Fermer'").click()
            print("Clicked 'Accepter & Fermer' button.")
        except Exception as e:
            print(f"Button not found or error clicking it: {e}")

        # Interact with the search input
        try:
            search_input = page.locator("input[placeholder='Rechercher sur leboncoin']").first
            search_input.wait_for(state="visible")
            search_input.click()
            print("Clicked on the search input.")

            # Fill the input with "nike" and press Enter
            search_input.fill("nike")
            print("Filled the search input with 'nike'.")
            search_input.press("Enter")
            print("Pressed Enter.")
        except Exception as e:
            print(f"Error interacting with the search input: {e}")

        # Take a screenshot
        page.screenshot(path="screenshot.png", full_page=True)

        # Get the page's HTML content
        html_content = page.content()
        browser.close()

        return html_content

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content, feed_class, item_class):
    soup = BeautifulSoup(body_content, "html.parser")

    # Remove scripts and styles
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Process links to append their href values
    for a in soup.find_all("a", href=True):
        a.insert_after(f" {a['href']}")  # Add the link after the anchor text

    # Initialize a list to hold cleaned articles
    cleaned_articles = []

    # Wrap and process each article with the specified class
    all_articles = soup.find(class_=feed_class)
    if all_articles:
        for article in all_articles.find_all(class_=item_class):
            # Get the text content of the article
            article_text = article.get_text(separator="\n")
            article_text = "\n".join(
                line.strip() for line in article_text.splitlines() if line.strip()
            )
            # Wrap the article text in <div> tags
            cleaned_articles.append(f"<div>{article_text}</div>")

    # Combine all articles with a separator
    cleaned_content = "\n".join(cleaned_articles)

    # Write the cleaned content to a new file
    with open("cleaned_content.txt", "w", encoding="utf-8") as file:
        file.write(cleaned_content)

    return cleaned_content


def split_dom_content(dom_content, max_length=3000):
    return [
        dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)
    ]


# Example usage
if __name__ == "__main__":
    website_url = "https://example.com"
    html = scrape_website(website_url)
    body = extract_body_content(html)
    clean_content = clean_body_content(body, feed_class="feed-class", item_class="item-class")
    print(split_dom_content(clean_content))