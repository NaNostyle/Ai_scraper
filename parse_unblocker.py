import json
import os
import dotenv
import streamlit as st
from pydantic import BaseModel, create_model
import ollama
from typing import List, Type
from openai import OpenAI

dotenv.load_dotenv()


# Create dynamic listing model using user-defined field names
def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:

    # Create field definitions using aliases for Field parameters
    field_definitions = {field: (str, ...) for field in field_names}
    # Dynamically create the model with all field
    return create_model('DynamicListingModel', **field_definitions)


def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:

    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))


# Constants for the prompt template
TEMPLATE = """
    You are to extract in the given JSON format the articles from a shop.
    Extract only the information needed no extra.
    This is chunk {current_chunk} of {total_chunks}. Beginning of markdown chunk : {dom_content} end of markdown chunk
"""


def parse_chunks(
        dom_chunks,
        DynamicListingsContainer,
        model,
        parse_function,
        output_dir='outputs',
):
    # This function handles chunk processing and saving the output in JSON format
    all_articles = []

    # Create a progress bar if required
    progress_bar = st.progress(0)

    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            # Format the prompt
            prompt = TEMPLATE.format(
                dom_content=chunk,
                current_chunk=i,
                total_chunks=len(dom_chunks),
            )

            # Call the parse function for specific handling
            validated_articles = parse_function(
                model=model, prompt=prompt, DynamicListingsContainer=DynamicListingsContainer
            )

            # Extend the list of all articles
            all_articles.extend([article.dict() for article in validated_articles.listings])

            # Update the progress bar
            progress_percentage = int((i / len(dom_chunks)) * 100)
            progress_bar.progress(progress_percentage)

        except Exception as e:
            print(f"Error in batch {i}: {e}")
            continue

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create output file path
    output_file = os.path.join(output_dir, f"{model}.json")

    # Write JSON to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, indent=4, ensure_ascii=False)

    print(f"Articles saved to {output_file}")

    return output_file


def ollama_parse_function(model, prompt, DynamicListingsContainer):

    try:
        # Generate chat response using Ollama
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": "You are to extract in the given JSON format the articles from a shop in the given JSON format"},
                {"role": "user", "content": prompt}
            ],
            format=DynamicListingsContainer.model_json_schema() # Corrected format to "json"
        )

        # Extract the content from the response
        result_json = response['message']['content']


        return result_json

    except Exception as e:
        print(f"Ollama parsing error: {e}")
        raise


def chatgpt_parse_function(model, prompt, DynamicListingsContainer):

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are to extract in the given JSON format the articles from a shop in the given JSON format"},
            {"role": "user", "content": prompt},
        ],
        response_format=DynamicListingsContainer
    )
    print(response.choices[0].message.parsed)
    return response.choices[0].message.parsed
    # Ensure dynamic_listing_model is used to validate parsed data

# Wrapper functions for Ollama and ChatGPT
def parse_with_ollama(dom_chunks,DynamicListingsContainer, model="llama3.2:1b", output_dir='output'):

    return parse_chunks(dom_chunks,DynamicListingsContainer, model, ollama_parse_function,
                        output_dir=output_dir)


def parse_with_chatgpt(dom_chunks,DynamicListingsContainer,  model="gpt-4o-mini", output_dir='output'):
    return parse_chunks(dom_chunks,DynamicListingsContainer, model, chatgpt_parse_function,
                        output_dir=output_dir)

