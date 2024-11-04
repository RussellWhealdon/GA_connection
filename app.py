import openai
import streamlit as st
import pandas as pd
from datetime import date
from ga4_data_pull import fetch_ga4_extended_data, summarize_acquisition_sources, summarize_landing_pages
from gsc_data_pull import fetch_search_console_data, summarize_search_queries
from llm_integration import load_model, query_gpt, initialize_llm_context

# Initialize LLM context with business context on app load
initialize_llm_context()

# Page configuration
st.set_page_config(
    page_title="Enhanced Google Analytics Data Dashboard",
    layout="wide"
)

st.title("Enhanced Google Analytics Data Analysis with GPT-4")

# Load and display data
ga_data = fetch_ga4_extended_data()
#st.write("Google Analytics Data")
#st.dataframe(ga_data)

search_data = fetch_search_console_data()
#st.write("Google Search Console Data")
#st.dataframe(search_data)

# Generate and display each summary with LLM analysis
def display_report_with_llm(summary_func, report_title, llm_prompt):
    st.subheader(report_title)
    
    # Generate summary
    summary = summary_func()
    st.write(summary)

    # Query LLM with specific prompt
    llm_response = query_gpt(llm_prompt, summary)
    st.write("GPT-4 Analysis:")
    st.write(llm_response)

# High-Level KPI Report
#display_report_with_llm(
#    lambda: create_ga_extended_summary(ga_data),
#    "High-Level KPI Report",
#    "Please analyze this high-level KPI report and provide insights and suggestions."
#)

# SEO Report
display_report_with_llm(
    lambda: summarize_search_queries(search_data),
    "Search Query SEO Report",
    "Based on this SEO report, provide suggestions on keyword optimization and content improvement."
)

# Traffic/Acquisition Report
display_report_with_llm(
    lambda: summarize_acquisition_sources(ga_data),
    "Traffic/Acquisition Report",
    "Analyze this acquisition report and provide insights on traffic sources and recommendations for improvement."
)

# Conversion Rate Analysis
display_report_with_llm(
    lambda: summarize_landing_pages(ga_data),
    "Conversion Rate Analysis",
    "Review this conversion rate report and suggest optimizations for improving lead generation and user engagement."
)

# User chat functionality for further questions
#st.subheader("Ask GPT-4 a Question")
#user_question = st.text_input("Enter your question:")

#if user_question:
#    response = query_gpt(user_question)
#    st.write("GPT-4 Response:")
#    st.write(response)
