from datetime import datetime
import json
from bs4 import BeautifulSoup
from pydantic import BaseModel, create_model
from typing import List, Type
from markdownify import MarkdownConverter
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def md(soup, **options):
    return MarkdownConverter(**options).convert_soup(soup)

def clean_body_content(html_content, container):
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = soup.body
    # Remove headers and footers based on common HTML tags or classes
    for element in body_content.find_all(['header', 'footer','id="seoFooter"']):
        element.decompose()
    seo_footer = body_content.find(id="seoFooter")
    if seo_footer:
        seo_footer.decompose()
    container = soup.find(class_=lambda c: c and container in c)

    if container:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_raw_data(md(container), timestamp)
        return md(container)
    else:
        return ""


import os


import os

def save_raw_data(raw_data, timestamp, output_folder='output', model="", llm=""):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    if llm:
        # Save as JSON when llm is specified
        raw_output_path = os.path.join(output_folder, f'rawData_{llm}-{model}-{timestamp}.json')
    else:
        # Save as Markdown when llm is not specified
        raw_output_path = os.path.join(output_folder, f'rawData_{timestamp}.md')

    # Save the file
    if llm:
        # Use json.dump for JSON data
        with open(raw_output_path, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=4, ensure_ascii=False)
    else:
        # Save Markdown data as string
        with open(raw_output_path, 'w', encoding='utf-8') as f:
            f.write(raw_data)

    print(f"Raw data saved to {raw_output_path}")
    return raw_output_path




def md(soup, **options):
    return MarkdownConverter(**options).convert_soup(soup)

def clean_body_content(html_content, container):
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = soup.body
    # Remove headers and footers based on common HTML tags or classes
    for element in body_content.find_all(['header', 'footer','id="seoFooter"']):
        element.decompose()
    seo_footer = body_content.find(id="seoFooter")
    if seo_footer:
        seo_footer.decompose()
    container = soup.find(class_=lambda c: c and container in c)

    if container:


        return md(container)
    else:
        return ""


import os


import os


def next_page_check(response) :
    soup= BeautifulSoup(response, 'html.parser')
    button = soup.find("button", {
        "data-spark-component": "pagination-next-trigger",
        "aria-disabled": "true"
    })

    if button:
        print("no next page")
        return False
    else:
        print("next page found")
        return True

def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    print(field_names)
    # Create field definitions using aliases for Field parameters
    field_definitions = {field: (str, ...) for field in field_names}
    # Dynamically create the model with all field
    return create_model('DynamicListingModel', **field_definitions)


def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:

    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

def split_markdown_content(dom_content, max_length=3000):
    return [
        dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)
    ]
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def save_to_mongodb(results,category,fields):
    # MongoDB connection URI
    uri = "mongodb+srv://nano:Nanojetaime47!@scraping.midrd.mongodb.net/?retryWrites=true&w=majority&appName=scraping&ssl=true"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Specify the database and collection
    db = client["scraping"]  # Database name
    collection = db[category]  # Collection name

    try:
        # Test the connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

        # Insert or update records using upsert
        inserted_count = 0

        if isinstance(results, list):  # Handle multiple documents
            for result in results:
                # Use upsert=True to insert if `ad_url` does not exist
                response = collection.update_one(
                    {"ad_url": result["ad_url"]},  # Query condition to match
                    {"$set": result},              # Fields to insert or update
                    upsert=True                    # Insert if no match is found
                )
                if response.upserted_id:  # Check if a new document was inserted
                    inserted_count += 1

            print(f"Successfully inserted or updated {inserted_count} unique documents into the database.")
        else:  # Handle a single document
            response = collection.update_one(
                {"ad_url": results["ad_url"]},  # Query condition to match
                {"$set": results},              # Fields to insert or update
                upsert=True                     # Insert if no match is found
            )
            if response.upserted_id:
                print("Successfully inserted 1 unique document into the database.")
            else:
                print("Document with the same ad_url already exists. Updated the existing record.")
        return f"Sucessfully inserted {inserted_count} in MongoDB"
    except Exception as e:
        print(f"An error occurred: {e}")





def save_to_google_sheet(results, category, fields):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = {
        "type": "service_account",
        "project_id": "nanomedia-348809",
        "private_key_id": "1198ec4822bd456d0b03261864341a0d220d3b8c",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCuDKCnprd2iDyT\nRcQhBt1BxyKA7EjiJwAZmzU1w442y25MJusk8pYBwHXaeN7+B+GrhteM2bsVL5hM\nA8Krb31fJXuooEfbJbdbUxWkaPR/2gK9Al5wi0o93QAAtzEpbHCIcdTF+sDs0lIP\nfgRD7DKpPSeOx+T/bhX0jNfmFXrNzTO2hAEq2dKyP+v080liHg0oQGd9YwLlw0Hc\nRB/kNI//aYhnO1Qmu2egSfiH0CU4NTmNAI7yfJNaXONvkMHbK7D0ajeob217cCo+\n5Y3daiENvH6U5VAx1RaoTbPa/fNqJwLPGZpkPZi0QZrmm7l9Wn4rjUEIayK4u9x6\nroQgf/aBAgMBAAECggEABr4E/DGcYkpZRGA7vobIS+vFpaZhlWcq3RMS3twONoev\nZGJOkh4WmwdEWXv8sW0HPDCLSZDGq0WueeVcZW06d1TZozjgR7hAj9haWoXZUNmW\naRF+LJBsxhQ5U43FKQRjIJn+QtQZpKLqHGEGk8YC2WT90w1hzNZMIe7Rzz8uRGoZ\n71XZY4OchSl6uUCGTmO5pFysJGlLW9k7+rTrtu4Oi+QMhKaPuADTibkkOn8w1blc\nedvzdnVFka49+PHkXRMos563fedzWGVmYbOUtq6OVioPu1XApZWFluqRDCO33+EK\nxPi1T5S6Sjv729J7YWLnVQhP3cg1bU2Kk2Kea8ufQQKBgQDg+aLbLLGQw7aGms0k\n6bY72Au2GGmDU9kppW0tF6tKs5BZN2XBSbTJqb+VKA7zcvupQ/WopVTq0I62I/pR\nEmbyqTExrnUZEOSzXPV1c1JLLqjS/S61lJzC/0dFF5tr98uJKRNoQvZi6GIFSewO\n9+6PhZw9Hl1tIK41zgltck3jcQKBgQDGDSRvPU5yNISET5yYSlHh5GeQlrgHIYWt\noqtx+DJNF1pkFLnuq0IbUt0uJLKQl0yNHKgL/5Zs0oclo1RceAvUrT6byGwZZD4x\n+bbHMFyno/8inbCBUg3h0k1Zl4TpwMQ62dTbqIWdtnfjrfIFijU7NxTy3QNG360P\nupDj6uucEQKBgQCSwWWB8cq282RatBqELMzKhulE1PHnUEgGCbqJQrpjVXUhLaj8\nCFedgVTPOL1gA660wPc8FvWo43lkyV1di1KKkuHbVcFfI4z8j/QytJKHJp3MXIoe\nux3zedEE+hxRtugXxiq5xYyyAoMGji0lqof9KZw8plUtfbcGtCukMH8skQKBgQCV\nUaVNpTg2zLe4ldlnzGjN2gnnLmtTHQgPcJy4UbuC+f9xg1rnwgEWXrRZrNtgPmI9\n5gQg/7NnGpdAXlMlYHDzCScyBrrRrg1iWnZe2WySDAg5DhDcf4Pt5UPiL2XLY0XP\nZRqh/f23ebIMW8IkQR5/JblKni1xSwTM3gmNfTnkMQKBgDJgDMkKUE6aXTtGr2Y8\niCaf/hm4vugKRyAz9xIWuahS2ok9yXGdJNCqWUY3hk4wmFXaqK1pynvFcbhhZfQg\n+GN31DCTSspyYZXFSeX1cZXZB04gWM3KsZ+crmWD1/v+RQ8rwvIUr5wRnbc6BO5F\nwQ9s8BrSR2Icjln84WIU9l6r\n-----END PRIVATE KEY-----\n",
        "client_email": "scraping@nanomedia-348809.iam.gserviceaccount.com",
        "client_id": "115404678841245839772",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/scraping%40nanomedia-348809.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet and get the specific sheet by name
    sheet = client.open("Leboncoin").worksheet(category)

    # Get all rows from the sheet (excluding the header)
    existing_ads = sheet.get_all_records()

    # Write header if the sheet is empty or if you want to overwrite it
    if not existing_ads:
        sheet.insert_row(fields, 1)

    # Check each result and append only if the ad_url doesn't exist
    for result in results:
        # Check if the ad_url already exists in the existing ads
        if not any(ad['ad_url'] == result.get("ad_url") for ad in existing_ads):
            row_to_insert = [result.get(field, "") for field in fields]  # Add all fields dynamically
            sheet.append_row(row_to_insert)
            print(f"Added {result.get('ad_url')}")
        else:
            print(f"Skipping {result.get('ad_url')} as it already exists.")

    return print("Google Sheet updated successfully!")