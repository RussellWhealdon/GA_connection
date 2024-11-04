import pandas as pd
from datetime import date
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
import streamlit as st

# Load the secrets for the service account path and property ID
service_account_info = st.secrets["google_service_account"]
property_id = st.secrets["google_service_account"]["property_id"]

# Initialize GA Client using the service account JSON
client = BetaAnalyticsDataClient.from_service_account_info(service_account_info)

# Get todays date
today = date.today().strftime("%Y-%m-%d")

# Function to fetch GA4 data with search queries, page path, and conversion data
def fetch_ga4_extended_data():
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="date"),                     # Break down by date
            Dimension(name="pagePath"),                 # Page path for performance by page
            Dimension(name="sessionSource"),            # Source where the session originated
            Dimension(name="firstUserCampaignName"),    # Campaign details, useful for origin analysis
            Dimension(name="firstUserSourceMedium"),    # Where people came from originally
            Dimension(name="landingPagePlusQueryString"),
            Dimension(name="eventName")
        ],
        metrics=[
            Metric(name="sessions"),                   # Total sessions
            Metric(name="screenPageViews"),            # Total page views
            Metric(name="bounceRate"),                 # Bounce rate
            Metric(name="averageSessionDuration"),     # Average session duration
            Metric(name="newUsers"),                   # New users
            Metric(name="eventCount")
        ],
        date_ranges=[DateRange(start_date="2024-01-01", end_date=today)],  # Define the date range
    )
    
    response = client.run_report(request)
    
    # Parse the response and create a DataFrame
    rows = []
    for row in response.rows:
        # Extract dimension and metric values
        date = row.dimension_values[0].value
        page_path = row.dimension_values[1].value
        session_source = row.dimension_values[2].value
        campaign_name = row.dimension_values[3].value
        source_medium = row.dimension_values[4].value
        lp_query = row.dimension_values[5].value
        event_name = row.dimension_values[6].value
            
        sessions = row.metric_values[0].value
        pageviews = row.metric_values[1].value
        bounce_rate = row.metric_values[2].value
        avg_session_duration = row.metric_values[3].value
        new_users = row.metric_values[4].value
        event_count = row.metric_values[5].value
        
        # Append the data to the list
        rows.append([
            date, page_path, session_source, campaign_name, source_medium, lp_query, event_name,
            sessions, pageviews, bounce_rate, avg_session_duration, new_users, event_count
        ])
    
    # Create DataFrame from the list of rows
    df = pd.DataFrame(rows, columns=[
        'Date', 'Page Path', 'Session Source', 'Campaign Name', 'Source/Medium', "Lp/Query", 'Event Name', 
        'Sessions', 'Pageviews', 'Bounce Rate', 'Avg. Session Duration', 'New Users', 'Event Count'
    ])
    
    # Process date columns for easier handling
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', inplace=True)

    # Filter rows where Event Name is "generate_lead" and create a new 'Leads' column
    df['Leads'] = df.apply(lambda row: float(row['Event Count']) if row['Event Name'] == "generate_lead" else 0, axis=1)

    return df

# Get summary of acquisition sources
def summarize_acquisition_sources(acquisition_data):
    # Check if required columns are in the dataframe
    required_cols = ["Session Source", "Sessions", "Bounce Rate", "Event Count"]
    if not all(col in acquisition_data.columns for col in required_cols):
        raise ValueError("Data does not contain required columns.")

    # Group by Session Source to get aggregated metrics
    source_summary = acquisition_data.groupby("Session Source").agg(
        Sessions=("Sessions", "sum"),
        Bounce_Rate=("Bounce Rate", "mean"),
        Conversions=("Event Count", "sum")
    ).reset_index()

    # Calculate Conversion Rate
    source_summary["Conversion Rate (%)"] = (source_summary["Conversions"] / source_summary["Sessions"] * 100).round(2)
    
    # Format summary text for LLM
    summary = "Traffic Source Performance Summary:\n"
    summary += "Source | Sessions | Avg. Bounce Rate (%) | Conversion Rate (%)\n"
    summary += "-" * 60 + "\n"

    for _, row in source_summary.iterrows():
        source = row["Session Source"]
        sessions = row["Sessions"]
        bounce_rate = row["Bounce_Rate"].round(2)
        conversion_rate = row["Conversion Rate (%)"]
        
        summary += f"{source} | {sessions} | {bounce_rate}% | {conversion_rate}%,\n"

    return summary

# Summarize landing pages
def summarize_landing_pages(acquisition_data):
    # Check if required columns are in the dataframe
    required_cols = ["Page Path", "Sessions", "Bounce Rate", "Event Count"]
    if not all(col in acquisition_data.columns for col in required_cols):
        raise ValueError("Data does not contain required columns.")

    # Group by Page Path to get aggregated metrics
    page_summary = acquisition_data.groupby("Page Path").agg(
        Sessions=("Sessions", "sum"),
        Bounce_Rate=("Bounce Rate", "mean"),
        Conversions=("Event Count", "sum")
    ).reset_index()

    # Calculate Conversion Rate
    page_summary["Conversion Rate (%)"] = (page_summary["Conversions"] / page_summary["Sessions"] * 100).round(2)
    
    # Format summary text for LLM
    summary = "Landing Page Performance Summary:\n"
    summary += "Page Path | Sessions | Avg. Bounce Rate (%) | Conversion Rate (%)\n"
    summary += "-" * 70 + "\n"

    for _, row in page_summary.iterrows():
        page_path = row["Page Path"]
        sessions = row["Sessions"]
        bounce_rate = row["Bounce_Rate"].round(2)
        conversion_rate = row["Conversion Rate (%)"]
        
        summary += f"{page_path} | {sessions} | {bounce_rate}% | {conversion_rate}%,\n"

    return summary
