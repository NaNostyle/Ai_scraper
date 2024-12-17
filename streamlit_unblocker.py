import streamlit as st
from streamlit import session_state
from streamlit_tags import st_tags_sidebar
from scrape_with_unblocker import scrape_website
from helper_functions import create_listings_container_model, create_dynamic_listing_model, split_markdown_content
from parse_with_llm import parse_with_chatgpt, parse_with_ollama
import json
import pandas as pd
from streamlit_toggle import st_toggle_switch
from scrape_website_auto import scrape_website_auto
# Initialize session_state variables if they don't exist
if "markdown" not in st.session_state:
    st.session_state.markdown = ""  # or None, depending on your logic
if "parsed_results" not in st.session_state :
    st.session_state.parsed_results = ""
if "all_parsed_results" not in st.session_state :
    st.session_state.all_parsed_results = ""
st.title("AI Web Scraper")
markdown = ""
with st.sidebar:
    url = st.text_input("Enter Website URL")
    fields = st_tags_sidebar(
        label='Enter Fields to Extract:',
        text='Press enter to add a tag',
        value=[],  # Default values if any
        suggestions=[],  # Keep empty for complete freedom
        maxtags=-1,  # Set to -1 for unlimited tags
        key='tags_input'
    )
    st.sidebar.markdown("---")
    container = st.text_input("Enter articles container class (e.g., styles_classifiedColumn)")
    st.session_state.url = url
    st.session_state.container = container
    st.session_state.fields = fields

    if st.session_state.url and st.session_state.container and st.session_state.fields:
        st.sidebar.markdown("---")
        if st.session_state.fields:
            dynamic_listing_model = create_dynamic_listing_model(st.session_state.fields)
            st.session_state.dynamic_listing_model = dynamic_listing_model
            dynamic_listing_container = create_listings_container_model(st.session_state.dynamic_listing_model)
            st.session_state.dynamic_listing_container = dynamic_listing_container
        auto_mode = st_toggle_switch(
            label="Auto mode",
            key="scraping_mode_toggle",
            default_value=False,  # Default to "Local"
            label_after=False,  # Display the label before the toggle
            inactive_color="#D3D3D3",
            active_color="#11567f",
            track_color="#29B5E8",
        )
        st.session_state.auto_mode = auto_mode
        if st.session_state.auto_mode == True and st.sidebar.button("Launch"):
            all_parsed_results = scrape_website_auto(st.session_state.url, st.session_state.container,st.session_state.dynamic_listing_container, model_option="gpt-4o-mini",llm_option="ChatGPT")
            st.session_state.all_parsed_results = all_parsed_results
        if st.session_state.auto_mode == False :
            if st.sidebar.button("Scrape Website") and not markdown :
                markdown = scrape_website(st.session_state.url, st.session_state.container)
                st.session_state.markdown = markdown
                dom_chunks = split_markdown_content(st.session_state.markdown)
                st.session_state.dom_chunks = dom_chunks
            if st.session_state.markdown or st.session_state.parsed_results:
                llm_option = st.radio("Choose LLM", ("ChatGPT", "Ollama"))
                st.session_state.llm_option = llm_option
                # Model selection based on LLM
                if st.session_state.llm_option == "ChatGPT":
                    model_option = st.radio("Choose model", ("gpt-4o-mini",))
                    st.session_state.model_option = model_option
                else:
                    model_option = st.radio("Choose model", ("llama3.2:latest", "llama3.2:1b", "codellama:latest"))
                    st.session_state.model_option = model_option
                    # Show the button to send to LLM
                if st.sidebar.button("Send to LLM"):
                    if st.session_state.llm_option == "ChatGPT":
                        parsed_results = parse_with_chatgpt(st.session_state.dom_chunks, st.session_state.dynamic_listing_container, st.session_state.model_option,llm_option)
                        st.session_state.parsed_results=parsed_results
                    else:
                        parsed_results = parse_with_ollama(st.session_state.dom_chunks, st.session_state.dynamic_listing_container, st.session_state.model_option,llm_option)
                        st.session_state.parsed_results = parsed_results
if session_state.parsed_results  :
    st.session_state.markdown =""
    parsed_data = []
    with open(session_state.parsed_results, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    if parsed_data:
        st.success("Parsing completed successfully!")
        st.write("Parsed Results:")
        df = pd.DataFrame(parsed_data)
        st.dataframe(df, height=800)
if session_state.all_parsed_results :
    st.session_state.parsed_results=""
    df = pd.DataFrame(session_state.all_parsed_results)
    st.dataframe(df, height=800)
if st.session_state.markdown:
    st.success("Scraped Successfully")
    st.write(st.session_state.markdown)