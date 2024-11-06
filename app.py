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

# Generate and display each summary with LLM analysis
def display_report_with_llm(summary_func, llm_prompt):
    # Generate summary
    summary = summary_func()

    # Query LLM with specific prompt
    llm_response = query_gpt(llm_prompt, summary)
    st.write("GPT-4 Analysis:")
    st.write(llm_response)

# Main function to handle the workflow
def main():
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
    st.markdown("<h3 style='text-align: center;'>Search Query Analysis</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Search query data** provides insights into the exact words or phrases people use when searching for content on search engines. By analyzing metrics like search terms, impressions, clicks, and average rank, businesses can understand which keywords drive traffic to their site and how they rank for specific searches.
        
        This data is particularly valuable for SEO and paid search optimization, as it highlights:
        - **Popular keywords** that attract visitors
        - **Click-through rates (CTR)** to assess engagement with search results
        - **Ranking position** to gauge visibility in search results.
        
        Using this information, a site owner can adjust content and keywords to improve search engine rankings, tailor marketing campaigns, and better reach their target audience.
        """)
        st.dataframe(search_data, use_container_width=True)
    with col2:
        response = display_report_with_llm(
            lambda: summarize_search_queries(search_data),
            """
            Based on this Search Query Report from Google give tips as to possible Paid Search Strategy and SEO optimization. Try to best answer the question, 
            What are people searching for when they come to my site and how can I get more of these users? Give me a brief analysis then 4 bullet points with 
            concrete tips for improvement. Limit this repsonse to ~ 200 words!
            """
        )
        st.write(str(response))
        # Store a message to pass to the SEO helper
        encoded_message = quote(response)
        url = f"https://smartmetric-seobuddy.streamlit.app?message={encoded_message}"
        st.write(f"[Go to SEO Helper with message]({url})")

    ### Display Acquisition Section
    st.divider()
    st.markdown("<h3 style='text-align: center;'>Summarize Acquisition Report</h3>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        **Acquisition Report** shows where visitors come from and how well these channels convert. It highlights:
        
        - **Traffic sources**: Details top channels like **Organic Search**, **Paid Search**, and **Social Media**.
        - **Engagement & conversion**: Provides metrics like **bounce rate** and **conversion rate** to evaluate quality.
        
        Key benefits:
        - **Optimize high-performing channels** for better conversions.
        - **Adjust strategies** for low-performing sources.
        - **Focus on high-conversion channels** to increase ROI.
        
        This helps refine marketing efforts to improve acquisition impact.
        """)
        st.dataframe(summarize_acquisition_sources(ga_data)[1], use_container_width=True)
    with col4:
        # Traffic/Acquisition Report
        display_report_with_llm(
            lambda: summarize_acquisition_sources(ga_data),
            """
            Analyze this acquisition report and provide insights on traffic sources and recommendations for improvement. Add insight as to how we might we might 
            improve the site based on this data. Give me a brief analysis then 4 bullet points with concrete tips for improvement. Limit this repsonse to ~ 200 words!
            """
        )
    st.divider()
    st.markdown("<h3 style='text-align: center;'>Landing Page Analysis</h3>", unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("""
        **Landing Page Overview** assesses each page's impact on engagement and conversions:
        
        - **Top pages**: Highlights content that draws users.
        - **Bounce rate**: Shows visitor retention per page.
        - **Session duration**: Indicates engagement time.
        - **Conversion rate**: Measures visitor actions, like form submissions.
        
        Use this to:
        - **Boost low-conversion, high-traffic pages**.
        - **Apply successful elements from top-converting pages**.
        - **Refine pages with high bounce rates**.
        
        This helps enhance content strategy for better engagement and conversions.
        """)
        st.dataframe(summarize_landing_pages(ga_data)[1], use_container_width=True)
    with col6:
        # Conversion Rate Analysis
        display_report_with_llm(
            lambda: summarize_landing_pages(ga_data),
            """
            Review this conversion rate report and suggest optimizations for improving lead generation and user engagement. Keep in mind that for someone to quantify 
            as a lead they need to go to the contacts page and fill out the form. So if landing page or source has a high conversion rate it means it ultimately led a user to the contacts page.
            Give me a brief analysis then 4 bullet points with concrete tips for improvement. Limit this repsonse to ~ 200 words!
            """
        )

    # Initialize the conversation history in session state if not already present
    if "conversation_history" not in st.session_state:
        st.session_state["conversation_history"] = []
    
    # Input field for the user to type a question
    user_question = st.text_input("Ask a follow-up question:")
    
    # Process the user question if entered
    if user_question:
        # Generate response from GPT-4 using the stored context
        llm_response = query_gpt(user_question)
        
        # Append the new question and response to the conversation history
        st.session_state["conversation_history"].append({"question": user_question, "response": llm_response})
    
    # Display the full conversation history
    st.subheader("Conversation History")
    for i, entry in enumerate(st.session_state["conversation_history"]):
        st.markdown(f"**User:** {entry['question']}")
        st.markdown(f"**GPT-4 Analysis:** {entry['response']}")
        st.markdown("---")  # Divider between each message


# Execute the main function only when the script is run directly
if __name__ == "__main__":
    main()
