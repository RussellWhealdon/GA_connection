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
    st.write("Search Query Analysis")
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
        display_report_with_llm(
            lambda: summarize_search_queries(search_data),
            "Search Query Analysis",
            """
            Based on this Search Query Report from Google give tips as to possible Paid Search Strategy and SEO optimization. Try to best answer the question, 
            What are people searching for when they come to my site and how can I get more of these users? Give me a brief analysis then 4 bullet points with 
            concrete tips for improvement. Limit this repsonse to ~ 200 words!
            """
        )

    ### Display Search Query Section
    st.divider()
    st.write("Summarize Acquisition Report Analysis")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        **Acquisition report** provides insights into where website visitors originate from and how effectively these channels drive conversions. By examining sources like organic search, paid search, social media, and direct traffic, the acquisition report reveals:
        
        - **Traffic sources**: Identifies which channels bring the most visitors, such as **Organic Search**, **Paid Search**, **Social Media**, or **Direct Traffic**.
        - **Engagement and conversion**: Shows metrics like **bounce rate**, **session duration**, and **conversion rate** to assess each source's quality and engagement level.
        
        This information helps in:
        - **Optimizing top-performing channels** to increase reach and conversions.
        - **Identifying underperforming sources** that may need budget adjustments or strategy changes.
        - **Focusing on high-conversion sources** to maximize ROI.
        
        This analysis empowers a business to tailor its marketing and outreach efforts, ensuring the highest impact from acquisition channels.
        """)
        st.dataframe(summarize_acquisition_sources(ga_data)[1], use_container_width=True)
    with col4:
        # Traffic/Acquisition Report
        display_report_with_llm(
            lambda: summarize_acquisition_sources(ga_data),
            "Traffic/Acquisition Report",
            """
            Analyze this acquisition report and provide insights on traffic sources and recommendations for improvement. Add insight as to how we might we might 
            improve the site based on this data. Give me a brief analysis then 4 bullet points with concrete tips for improvement. Limit this repsonse to ~ 200 words!
            """
        )
    st.divider()
    st.write("Summarize Landing Page Analysis")
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("""
        **Landing Page Overview** provides a snapshot of how each landing page on the website performs regarding user engagement and conversions. This overview assesses individual page effectiveness by examining:
        
        - **Top landing pages**: Identifies the most visited pages, helping understand which content draws users initially.
        - **Bounce rate**: Measures the percentage of visitors who leave after viewing a single page, giving insight into each page’s ability to retain user interest.
        - **Average session duration**: Tracks the time users spend on each page, indicating engagement levels.
        - **Conversion rate**: Shows the percentage of visitors who complete desired actions, such as form submissions, starting from each page.
        
        This analysis is helpful for:
        - **Improving high-traffic, low-conversion pages** to capture more leads.
        - **Highlighting high-conversion pages** to understand and replicate successful elements.
        - **Identifying pages with high bounce rates** that may need optimization for content, design, or relevance.
        
        This overview helps a business refine its website’s structure and content strategy, ensuring key pages maximize user engagement and conversion potential.
        """)
        st.dataframe(summarize_landing_pages(ga_data)[1], use_container_width=True)
    with col6:
        # Conversion Rate Analysis
        display_report_with_llm(
            lambda: summarize_landing_pages(ga_data),
            "Conversion Rate Analysis",
            """
            Review this conversion rate report and suggest optimizations for improving lead generation and user engagement. Keep in mind that for someone to quantify 
            as a lead they need to go to the contacts page and fill out the form. So if landing page or source has a high conversion rate it means it ultimately led a user to the contacts page.
            Give me a brief analysis then 4 bullet points with concrete tips for improvement. Limit this repsonse to ~ 200 words!
            """
        )

# Execute the main function only when the script is run directly
if __name__ == "__main__":
    main()
