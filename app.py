import openai
import streamlit as st
import pandas as pd
from datetime import date
from ga4_data_pull import fetch_ga4_extended_data, summarize_acquisition_sources, summarize_landing_pages
from gsc_data_pull import fetch_search_console_data, summarize_search_queries
from llm_integration import initialize_llm_context, query_gpt

# Initialize LLM context with business context on app load
initialize_llm_context()

# Page configuration
st.set_page_config(
    page_title="Enhanced Google Analytics Data Dashboard",
    layout="wide"
)

# Generate and display each summary with LLM analysis
def display_report_with_llm(summary_func, report_title, llm_prompt):
    st.subheader(report_title)

    # Generate summary
    summary = summary_func()

    # Query LLM with specific prompt
    llm_response = query_gpt(llm_prompt, summary)
    st.write("GPT-4 Analysis:")
    st.write(llm_response)

# Main function to handle the workflow
def main():
    st.title("Enhanced Google Analytics Data Analysis with GPT-4")

    # Load and display data
    ga_data = fetch_ga4_extended_data()
    # st.write("Google Analytics Data")
    # st.dataframe(ga_data)

    search_data = fetch_search_console_data()
    # st.write("Google Search Console Data")
    # st.dataframe(search_data)

    # High-Level KPI Report
    # display_report_with_llm(
    #     lambda: create_ga_extended_summary(ga_data),
    #     "High-Level KPI Report",
    #     "Please analyze this high-level KPI report and provide insights and suggestions."
    # )

    ### Display Search Query Section
    st.divider()
    st.write("Google Search Console Data")
    col1, col2 = st.columns(2)
    st.write("Search Query Analysis")
    with col1:
        st.dataframe(search_data, use_container_width=True)
    
    with col2:
        st.write("Example text")
    # SEO Report
    # display_report_with_llm(
    #     lambda: summarize_search_queries(search_data),
    #     "Search Query Analysis",
    #     """
    #     Based on this Search Query Report from Google give tips as to possible Paid Search Strategy and SEO optimization. Try to best answer the question, 
    #     What are people searching for when they come to my site and how can I get more of these users? Give me a brief analysis then 4 bullet points with concrete tips for improvement.
    #     """
    # )

    ### Display Search Query Section
    st.divider()
    #st.dataframe(search_data)
    st.write("Summarize Acquisition Report Analysis")
    # # Traffic/Acquisition Report
    # display_report_with_llm(
    #     lambda: summarize_acquisition_sources(ga_data),
    #     "Traffic/Acquisition Report",
    #     """
    #     Analyze this acquisition report and provide insights on traffic sources and recommendations for improvement. Add insight as to how we might we might 
    #     improve the site based on this data. Give me a brief analysis then 4 bullet points with concrete tips for improvement.
    #     """
    # )

    st.divider()
    st.write("Summarize Landing Page Analysis")
    # # Conversion Rate Analysis
    # display_report_with_llm(
    #     lambda: summarize_landing_pages(ga_data),
    #     "Conversion Rate Analysis",
    #     """
    #     Review this conversion rate report and suggest optimizations for improving lead generation and user engagement. Keep in mind that for someone to quantify 
    #     as a lead they need to go to the contacts page and fill out the form. So if landing page or source has a high conversion rate it means it ultimately led a user to the contacts page.
    #     Give me a brief analysis then 4 bullet points with concrete tips for improvement. 
    #     """

    
    #)

# Execute the main function only when the script is run directly
if __name__ == "__main__":
    main()
