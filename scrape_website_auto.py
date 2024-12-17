from helper_functions import clean_body_content, next_page_check,split_markdown_content,save_raw_data
from parse_with_llm import parse_with_chatgpt
import json
from unidecode import unidecode
from datetime import datetime
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Example of using urllib to fetch a webpage

def scrape_website_auto(base_url, container, dynamic_listing_container, model_option, llm_option):
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
            f = open("web-unlocker.html", "w")
            f.write(str(html))
            f.close()

            # Clean the body content and add to container
            markdown = clean_body_content(html, container)
            dom_chunks = split_markdown_content(unidecode(markdown))

            # Parse the chunks with ChatGPT
            output_file = parse_with_chatgpt(
                dom_chunks,
                dynamic_listing_container,
                model_option,
                llm_option
            )

            # Read the JSON content from the file
            with open(output_file, 'r', encoding='utf-8') as f:
                parsed_content = json.load(f)
                all_results.extend(parsed_content)  # Append parsed JSON data to the list

            # Check if there's a next page
            next_page = next_page_check(html)
            page += 1  # Increment page number

        except Exception as e:
            print(f"Error occurred: {e}")
            break
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_raw_data(
        raw_data=all_results,  # Use json.dumps to get a JSON string
        timestamp=timestamp,
        output_folder="leboncoin/all_results",
        model=model_option,
        llm=llm_option
    )
    print(all_results, "All parsed results")
    return all_results