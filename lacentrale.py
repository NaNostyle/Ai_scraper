import os
from seleniumbase import SB

# Define the script directory for user data
script_dir = os.path.dirname(os.path.abspath(__file__))
userdata_dir = os.path.join(script_dir, "Jean")

def scrape_lacentrale(brand="renault", modele="espace", annee="2024"):
    with SB(uc=True, user_data_dir="Jean", headless=True) as sb:
        try:
            # Open the constructed URL
            sb.uc_open_with_reconnect(f"https://www.lacentrale.fr/cote-voitures-{brand}-{modele}--{annee}-.html")
            sb.sleep(3)

            # XPath to locate all <a> links with the given model and year in their href
            xpath = f'//a[contains(@href, "{modele}") and contains(@href, "{annee}")]'

            # Find all matching links
            links = sb.find_elements(xpath)
            if links:
                last_link = links[-1]  # Get the last matching link
                last_link.click()      # Click the WebElement directly
                print("Last link clicked successfully!")
            else:
                print("No matching links found on the page.")
                  # Quit the browser if the link is not found
                return "No matching links"  # Return a failure message

            # XPath to locate the price element
            price_xpath = '//div[starts-with(@class, "QuotationDetail")]'
            price_element = sb.find_element(price_xpath)
            price_text = price_element.text  # Extract the text from the element

            return price_text



        except Exception as e:
            print(f"An error occurred: {e}")
            sb.driver.quit()  # Quit the browser if any error occurs
            return "Error occurred"
