import requests
from helper_functions import clean_body_content,next_page_check
def scrape_website(url,container) :
    proxies={'http': 'http://brd-customer-hl_f2e06bf4-zone-web_unlocker:sjoucztfmb0c@brd.superproxy.io:33335',
            'https': 'http://brd-customer-hl_f2e06bf4-zone-web_unlocker:sjoucztfmb0c@brd.superproxy.io:33335'}
    # Create a session
    response = requests.get(url,proxies=proxies,verify=False)
    return clean_body_content(response.text,container)




