import json
import os
import dotenv
import streamlit as st
import ollama
from openai import OpenAI
from helper_functions import save_raw_data
dotenv.load_dotenv()
from datetime import datetime

# Create dynamic listing model using user-defined field names


# Constants for the prompt template
system_prompt = """"You are a structured data extraction assistant. Your task is to extract product information from shop HTML in a specific JSON format. 
                    Your behavior:
                    - Follow instructions provided by the user strictly.
                    - Extract only the required fields (e.g., name, price, URL) according to the JSON schema provided.
                    - Validate the extracted JSON to ensure it is well-formed and adheres to the schema.
                    - Never add extra details, summaries, or explanations. Only return the requested JSON output.
                    - In case of errors, correct them and revalidate before responding. 
                    - if the model and the brand are required you will find them in the title. If you don't find them you do not take in account this entry                                                """

TEMPLATE = """
                    You are tasked to extract product listings from a shop's DOM. 
                    
                    Input: HTML chunk (in markdown format). 
                    Task: Identify all product listings in this chunk and extract the necessary information
                    Rules:
                    1. Return only the extracted data, formatted as JSON
                    2. Do not add any extra fields, descriptions, or comments.
                    3. Validate the JSON before returning it. Ensure it is well-formed and matches the schema.     
                    Process each chunk individually. This is chunk {current_chunk} of {total_chunks}.
                    Beginning of markdown chunk:
                    {dom_content}
                    End of markdown chunk.
"""


def parse_chunks(
        dom_chunks,
        DynamicListingsContainer,
        model_option,
        parse_function,
        llm_option,
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
                model=model_option, prompt=prompt, DynamicListingsContainer=DynamicListingsContainer
            )

            # Extend the list of all articles
            all_articles.extend([article.dict() for article in validated_articles.listings])

            # Update the progress bar
            progress_percentage = int((i / len(dom_chunks)) * 100)
            progress_bar.progress(progress_percentage)

        except Exception as e:
            print(f"Error in batch {i}: {e}")
            continue
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = save_raw_data(
        raw_data=all_articles,  # Use json.dumps to get a JSON string
        timestamp=timestamp,
        output_folder="output",
        model=model_option,
        llm=llm_option
    )
    # Write JSON to file

    return output_file


def ollama_parse_function(model, prompt, DynamicListingsContainer):
    all_articles = []
    # Generate chat response using Ollama
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        format=DynamicListingsContainer.model_json_schema()  # Use standard JSON format
    )

    # Extract the content from the response and parse it into a Python object
    result_json = response['message']['content']
    print(f"Raw response JSON: {result_json}")
    parsed_result = json.loads(result_json)
    validated_articles = DynamicListingsContainer(**parsed_result)
    print(validated_articles,"validated_articles")
    return validated_articles



def chatgpt_parse_function(model, prompt, DynamicListingsContainer):

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        response_format=DynamicListingsContainer
    )
    print("Final dynamic listings:", response.choices[0].message.parsed)
    return response.choices[0].message.parsed
    # Ensure dynamic_listing_model is used to validate parsed data

# Wrapper functions for Ollama and ChatGPT
def parse_with_ollama(dom_chunks,DynamicListingsContainer, model_option="llama3.2:lastest", output_dir='output',llm_option="ollama"):

    return parse_chunks(dom_chunks,DynamicListingsContainer, model_option, ollama_parse_function,llm_option,
                        output_dir=output_dir,)


def parse_with_chatgpt(dom_chunks,DynamicListingsContainer,  model_option="gpt-4o-mini", output_dir='output',llm_option="ChatGPT"):
    return parse_chunks(dom_chunks,DynamicListingsContainer, model_option, chatgpt_parse_function,llm_option,
                        output_dir=output_dir,)

