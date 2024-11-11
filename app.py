import openai
import streamlit as st
import pandas as pd
from datetime import date
from ga4_data_pull import fetch_ga4_extended_data, summarize_acquisition_sources, summarize_landing_pages
from gsc_data_pull import fetch_search_console_data, summarize_search_queries
from llm_integration import initialize_llm_context, query_gpt
from urllib.parse import quote

# Page configuration
st.set_page_config(page_title="BizBuddy", layout="wide", page_icon = "🤓")

st.markdown("<h1 style='text-align: center;'>Welcome to Bizness Buddy</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Let's take your business to the next level</h4>", unsafe_allow_html=True)


# Initialize LLM context with business context on app load
initialize_llm_context()

# Generate and display each summary with LLM analysis
def display_report_with_llm(summary_func, llm_prompt):
    # Generate summary
    summary = summary_func()

    # Query LLM with specific prompt
    llm_response = query_gpt(llm_prompt, summary)
    return llm_response

def main():

    #Seperate different sections of the website
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h2 style='text-align: center;'>Web Performance Overview</h2>", unsafe_allow_html=True)
        


# Execute the main function only when the script is run directly
if __name__ == "__main__":
    main()
