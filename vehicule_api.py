import requests

BASE_URL = "https://www.carqueryapi.com/api/0.3/"

params = {
    "cmd": "getMakes",  # Example command to get makes
    "year": 2023,       # Optional: specify a year
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    print("Car Makes:")
    for make in data["Makes"]:
        print(f"- {make['make_display']} ({make['make_country']})")
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")