from helper_functions import clean_body_content, next_page_check,split_markdown_content,create_dynamic_listing_model,create_listings_container_model
from parse_with_llm import parse_with_chatgpt
import json
from unidecode import unidecode
from datetime import datetime
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Example of using urllib to fetch a webpage
base_url = "https://www.leboncoin.fr/recherche?text=brouette&locations=Agen_47000__44.20213_0.62055_3171_20000&sort=time" #fetch dynamically
container = "styles_classifiedColumn" #fetch dynamically
fields =['price', 'ad_url'] #fetched dynamically
dynamic_listing_model = create_dynamic_listing_model(fields)
dynamic_listing_container = create_listings_container_model(dynamic_listing_model)
def scrape_website_auto(base_url, container, dynamic_listing_container, model_option="gpt-4o-mini",llm_option="ChatGPT"):
    proxies = {
        'http': 'http://brd-customer-hl_f2e06bf4-zone-web_unlocker:sjoucztfmb0c@brd.superproxy.io:33335',
        'https': 'http://brd-customer-hl_f2e06bf4-zone-web_unlocker:sjoucztfmb0c@brd.superproxy.io:33335'
    }

    page = 1
    next_page = True
    all_results = []  # This will store all parsed JSON content

    while next_page:
        # Update URL with the current page number
        url = f"{base_url}&page={page}"
        print(f"Scraping: {url}")

        try:
            # Make the request
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({
                    'http': 'http://brd-customer-hl_f2e06bf4-zone-web_unlocker:sjoucztfmb0c@brd.superproxy.io:33335',
                    'https': 'http://brd-customer-hl_f2e06bf4-zone-web_unlocker:sjoucztfmb0c@brd.superproxy.io:33335'
                }

                )
            )
            html = opener.open(
                url).read()

            # Clean the body content and add to container
            markdown = clean_body_content(html, container)
            dom_chunks = split_markdown_content(unidecode(markdown))

            # Parse the chunks with ChatGPT
            parsed_content = parse_with_chatgpt(
                dom_chunks,
                dynamic_listing_container,
                model_option,
                llm_option
            )
            all_results.extend(parsed_content)
            # Check if there's a next page
            next_page = next_page_check(html)
            page += 1  # Increment page number

        except Exception as e:
            print(f"Error occurred: {e}")
            break
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(all_results, "All parsed results")
    return all_results