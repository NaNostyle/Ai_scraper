import requests
import json
import asyncio
import aiohttp
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI
import os
import dotenv
import streamlit as st

dotenv.load_dotenv()

from pydantic import BaseModel, constr
from typing import List, Optional

class Article(BaseModel):
    item_url: str # Ensure URL starts with 'https://www.vinted.fr/items'
    price_incl: int
    nickname: str
    sizes: Optional[List[str]] = None  # Optional field with a default of None
    brand: str
    member_url: str
    condition: Optional[str] = None  # Optional field with a default of None

# Define a model for the overall response
class Articles(BaseModel):
    articles: List[Article]

# Base URL of the Ollama server
OLLAMA_URL = "http://localhost:11434/api/chat"

# Template for parsing instructions
template = (
    """
    you are to extract the articles from a file. Each article item details begin with a <div> and en with a </div>
    This is chunk {current_chunk} of {total_chunks}. Beginning of articles : {dom_content} end of markdown chunk 
    Please provide a json output from the markdown chunks
    """
)


# Function to make the request
def parse_with_ollama(
        dom_chunks,
        model="llama3.2",
):
    """
    Parse DOM chunks using Ollama's structured output capabilities
    """
    all_articles = []

    # Create a progress bar in Streamlit
    progress_bar = st.progress(0)  # Initial progress is 0%

    # Template for parsing instructions
    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            # Format the prompt
            prompt = template.format(
                dom_content=chunk,
                current_chunk=i,
                total_chunks=len(dom_chunks),
            )

            # Prepare the payload
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "format": Articles.model_json_schema()  # Use the model's JSON schema
            }

            # Make the request to the Ollama server
            response = requests.post(OLLAMA_URL, json=payload)

            # Update the progress bar with percentage completion
            progress_percentage = int((i / len(dom_chunks)) * 100)
            progress_bar.progress(progress_percentage)  # Update progress bar

            # Handle response
            if response.status_code == 200:
                # Extract and parse the JSON response
                result_json = response.json().get("message", {}).get("content", "")
                parsed_result = json.loads(result_json)

                # Validate the parsed result
                validated_articles = Articles(**parsed_result)

                # Extend the list of all articles
                all_articles.extend(validated_articles.articles)
            else:
                print(f"Error in batch {i}: {response.status_code}, {response.text}")
                continue

        except Exception as e:
            print(f"Unexpected error in batch {i}: {e}")
            continue

    # Convert to JSON using the Pydantic model's json method
    articles_data = Articles(articles=all_articles)
    json_output = articles_data.model_dump_json(indent=4)

    # Return the JSON output
    return json_output


def parse_with_chatgpt(
        dom_chunks,
        api_key=None,
        model="gpt-4o-mini",
):
    """
    Parse DOM chunks using OpenAI's structured output capabilities
    """
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    all_articles = []

    # Create a progress bar in Streamlit
    progress_bar = st.progress(0)  # Initial progress is 0%

    # Template for parsing instructions
    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            # Format the prompt
            prompt = template.format(
                dom_content=chunk,
                current_chunk=i,
                total_chunks=len(dom_chunks),
            )

            # Make API call with structured output
            response = client.beta.chat.completions.parse(
                model=model,
                response_format=Articles,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt}
                ],
            )

            # Extract and parse the JSON response
            result_json = response.choices[0].message.content
            parsed_result = json.loads(result_json)

            # Validate the parsed result
            validated_articles = Articles(**parsed_result)

            # Extend the list of all articles
            all_articles.extend(validated_articles.articles)

            # Update the progress bar with percentage completion
            progress_percentage = int((i / len(dom_chunks)) * 100)
            progress_bar.progress(progress_percentage)  # Update progress bar

        except Exception as e:
            print(f"Unexpected error in batch {i}: {e}")
            continue

    articles_data = Articles(articles=all_articles)

    # Convert to JSON using the Pydantic model's json method
    json_output = articles_data.model_dump_json(indent=4)

    # Return the JSON output
    return json_output