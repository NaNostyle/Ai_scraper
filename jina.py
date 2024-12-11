import requests

def jina_request(url):
    headers = {
        'X-Retain-Images': 'none',
        "X-Target-Selector": ".new-item-box__container",
    }

    # Format the URL correctly
    full_url = f"https://r.jina.ai/{url}"

    # Make the request
    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Debug: Print response status
        print(f"Request successful: {response.status_code}")

        # Remove all line breaks from the response text
        processed_text = response.text.replace("\n", "").strip()

        # Write the processed text to a file named 'jna.md'
        with open("jina.md", "w", encoding="utf-8") as file:
            file.write(processed_text)

        print(processed_text)
        return processed_text

    except requests.exceptions.RequestException as e:
        # Handle request-related errors
        print(f"Request failed: {e}")
        return None