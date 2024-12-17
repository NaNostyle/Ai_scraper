from helper_functions import clean_body_content, next_page_check,split_markdown_content,save_raw_data,create_dynamic_listing_model,create_listings_container_model
from parse_with_llm import parse_with_chatgpt
import json
from unidecode import unidecode
from datetime import datetime
import urllib.request
import ssl
from lacentrale import scrape_lacentrale
import re
ssl._create_default_https_context = ssl._create_unverified_context

# Example of using urllib to fetch a webpage
# base_url = "https://www.leboncoin.fr/recherche?category=2&locations=Bordeaux_33300__44.89146_-0.56392_5000_5000&price=1000-3000" #fetch dynamically
# container = "styles_classifiedColumn" #fetch dynamically
# fields =['price', 'ad_url',"annee","kilometrage","carburant","boite de vitesse","title","modele","marque"] #fetched dynamically
# dynamic_listing_model = create_dynamic_listing_model(fields)
# dynamic_listing_container = create_listings_container_model(dynamic_listing_model)
def scrape_website_auto(base_url, container, dynamic_listing_container, model_option="gpt-4o-mini",llm_option="ChatGPT"):
    def extract_price(price_text):
        # Regular expression to match the price pattern like "2 479 €"
        match = re.search(r"(\d[\d\s]*\d) €", price_text)  # Matches numbers with possible spaces and the euro symbol
        if match:
            return match.group(1).replace(" ",
                                          "")  # Return the cleaned price without non-numeric characters like spaces
        return None
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
            # next_page = next_page_check(html)
            next_page=False
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
    for result in all_results:
        # Check if 'modele', 'marque', and 'annee' are present and not empty
        if result.get("modele") and result.get("marque") and result.get("annee"):
            brand = result["marque"]
            modele = result["modele"]
            annee = result["annee"]
            print(modele)
            print(brand)
            print(annee)

            # Call scrape_lacentrale and print result
            price_text = scrape_lacentrale(brand=brand, modele=modele, annee=annee)
            cleaned_price = extract_price(price_text)
            print(
                f"Pour l'annonce http://www.leboncoin.fr{result['ad_url']}, la côte est de {cleaned_price} pour un prix de vente de {result['price']}")
        else:
            print("Missing required fields in the result:", result)

    return all_results

scrape_website_auto(base_url, container, dynamic_listing_container, model_option="gpt-4o-mini",llm_option="ChatGPT")