import streamlit as st
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from parse import parse_with_ollama, parse_with_chatgpt

# Streamlit UI
st.title("AI Web Scraper")
url = st.text_input("Enter Website URL")

# Step 1: Let user input the dynamic class names for articles and container
feed_class = st.text_input("Enter the class for the feed (e.g., 'feed-grid' 'styles_Listing__isoog'")
item_class = st.text_input("Enter the class for the item (e.g., 'new-item-box__container' 'styles_adCard__JzKik')")

# Step 2: Scrape the Website when the button is clicked
if st.button("Scrape Website"):
    if url and feed_class and item_class:
        st.write("Scraping the website...")

        # Scrape the website
        dom_content = scrape_website(url)
        body_content = extract_body_content(dom_content)

        # Clean the content based on the dynamic class names
        cleaned_content = clean_body_content(body_content, feed_class, item_class)

        # Store the DOM content in Streamlit session state
        st.session_state.dom_content = cleaned_content

        with st.expander("View DOM Content"):
            st.text_area("DOM Content", st.session_state.dom_content, height=300)
        st.write(f"{url} scraped")
    else:
        st.error("Please enter all required fields (URL and classes).")

# Step 3: Parse the content based on user choice
if "dom_content" in st.session_state:
    parser_option = st.radio("Choose Parser", ("ChatGPT", "Ollama"))

    if st.button("Parse Content"):
        st.write("Parsing the content...")

        # Split the DOM content into chunks
        dom_chunks = split_dom_content(st.session_state.dom_content)

        # Parse the content based on the selected option
        if parser_option == "ChatGPT":
            parsed_result = parse_with_chatgpt(dom_chunks)
        else:
            parsed_result = parse_with_ollama(dom_chunks)

        st.write(parsed_result)