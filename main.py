import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from functools import wraps

# Import your functions and classes
from helper_functions import create_dynamic_listing_model, create_listings_container_model,save_to_mongodb,save_to_google_sheet
import ssl
from leboncoin_lacentrale_main import scrape_website_auto

# SSL setup
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables from .env file
load_dotenv()

# Flask app setup
app = Flask(__name__)

# API key decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if api_key is None or api_key != os.getenv("API_KEY"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Wrap your scraper function in an API route with API key protection
@app.route("/scrape", methods=["POST"])
@require_api_key  # Protect the route with the API key check
def scrape():
    try:
        # Extract parameters from the request body (if needed)
        base_url = request.json.get("base_url")
        fields = request.json.get("fields")
        category = request.json.get("category")
        # Create dynamic models
        dynamic_listing_model = create_dynamic_listing_model(fields)
        dynamic_listing_container = create_listings_container_model(dynamic_listing_model)
        container = "styles_classifiedColumn"
        # Call your scraper
        results = scrape_website_auto(
            base_url, container, dynamic_listing_container,
            model_option="gpt-4o-mini", llm_option="ChatGPT"
        )
        success = save_to_mongodb(results, category,fields)
        save_to_google_sheet(results,category,fields)
        if results:
            print("Success:", results)
        else:
            print("No results found.")
        print(success)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint (required by Render)
@app.route("/")
def health_check():
    return "App is running", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 locally
    app.run(host="0.0.0.0", port=port)