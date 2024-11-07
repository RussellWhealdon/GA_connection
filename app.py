import openai
import streamlit as st
import pandas as pd
from datetime import date
from ga4_data_pull import fetch_ga4_extended_data, summarize_acquisition_sources, summarize_landing_pages
from gsc_data_pull import fetch_search_console_data, summarize_search_queries
from llm_integration import initialize_llm_context, query_gpt
from urllib.parse import quote

# Page configuration
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>Chelsea Whealdon Nutrition Website Helper</h1>", unsafe_allow_html=True)

# Initialize LLM context with business context on app load
initialize_llm_context()

# Cache data fetching functions
@st.cache_data
def get_ga_data():
    return fetch_ga4_extended_data()

@st.cache_data
def get_search_data():
    return fetch_search_console_data()

# Generate and display each summary with LLM analysis
def display_report_with_llm(summary_func, llm_prompt):
    summary = summary_func()
    llm_response = query_gpt(llm_prompt, summary)
    return llm_response

# Main function to handle the workflow
def main():
    # Load data
    ga_data = get_ga_data()
    search_data = get_search_data()

    ### Search Query Section
    st.divider()
    st.markdown("<h3 style='text-align: center;'>Search Query Analysis</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Search query data** provides insights into search behavior and highlights opportunities for SEO and paid search optimization.
        """)
        st.dataframe(search_data, use_container_width=True)
    with col2:
        response = display_report_with_llm(
            lambda: summarize_search_queries(search_data),
            "Based on this Search Query Report from Google..."
        )
        st.write(response)
        encoded_message = quote(str(response))
        url = f"https://smartmetric-seobuddy.streamlit.app?message={encoded_message}"
        st.link_button("Check Out our SEO Helper!!", url)

    ### Acquisition Report Section
    st.divider()
    st.markdown("<h3 style='text-align: center;'>Summarize Acquisition Report</h3>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        st.dataframe(summarize_acquisition_sources(ga_data)[1], use_container_width=True)
    with col4:
        st.write(display_report_with_llm(
            lambda: summarize_acquisition_sources(ga_data),
            "Analyze this acquisition report..."
        ))

    ### Landing Page Analysis Section
    st.divider()
    st.markdown("<h3 style='text-align: center;'>Landing Page Analysis</h3>", unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        st.dataframe(summarize_landing_pages(ga_data)[1], use_container_width=True)
    with col6:
        st.write(display_report_with_llm(
            lambda: summarize_landing_pages(ga_data),
            "Review this landing page report..."
        ))

    ### Chat Section
    st.divider()
    st.markdown("<h3 style='text-align: center;'>Ask a Question</h3>", unsafe_allow_html=True)

    # Initialize conversation history
    if "conversation_history" not in st.session_state:
        st.session_state["conversation_history"] = []

    # Input field for the user to type a question
    user_question = st.text_input("Ask a follow-up question:")

    # Process the user question if entered
    if user_question and st.button("Submit"):
        llm_response = query_gpt(user_question)
        st.session_state["conversation_history"].append({"question": user_question, "response": llm_response})

    # Display the full conversation history
    st.subheader("Conversation History")
    for entry in st.session_state["conversation_history"]:
        st.markdown(f"**User:** {entry['question']}")
        st.markdown(f"**GPT-4 Analysis:** {entry['response']}")
        st.markdown("---")

# Execute the main function only when the script is run directly
if __name__ == "__main__":
    main()
