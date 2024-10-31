import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
import streamlit as st

# Load the secrets for the service account path and property ID
service_account_info = st.secrets["google_service_account"]
property_id = st.secrets["google_service_account"]["property_id"]

# Initialize GA Client using the service account JSON
client = BetaAnalyticsDataClient.from_service_account_info(service_account_info)

# Function to fetch GA4 data with search queries, page path, and conversion data
def fetch_ga4_extended_data():
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="date"),                     # Break down by date
            Dimension(name="pagePath"),                 # Page path for performance by page
            Dimension(name="sessionSource"),            # Source where the session originated
            Dimension(name="searchTerm"),               # Search query terms
            Dimension(name="firstUserCampaignName"),    # Campaign details, useful for origin analysis
            Dimension(name="firstUserSourceMedium"),    # Where people came from originally
            Dimension(name="landingPagePlusQueryString")
        ],
        metrics=[
            Metric(name="sessions"),                   # Total sessions
            Metric(name="screenPageViews"),            # Total page views
            Metric(name="keyEvents:Lead"),               # Lead conversion metric
            Metric(name="bounceRate"),                 # Bounce rate
            Metric(name="averageSessionDuration"),     # Average session duration
            Metric(name="newUsers"),                   # New users
        ],
        date_ranges=[DateRange(start_date="2024-09-01", end_date="2024-10-25")],  # Define the date range
    )
    
    response = client.run_report(request)
    
    # Parse the response and create a DataFrame
    rows = []
    for row in response.rows:
        # Extract dimension and metric values
        date = row.dimension_values[0].value
        page_path = row.dimension_values[1].value
        session_source = row.dimension_values[2].value
        search_term = row.dimension_values[3].value
        campaign_name = row.dimension_values[4].value
        source_medium = row.dimension_values[5].value
        Lp_Query = row.dimension_values[6].value
        
        sessions = row.metric_values[0].value
        pageviews = row.metric_values[1].value
        leads = row.metric_values[2].value
        bounce_rate = row.metric_values[3].value
        avg_session_duration = row.metric_values[4].value
        new_users = row.metric_values[5].value
        
        # Append the data to the list
        rows.append([
            date, page_path, session_source, search_term, campaign_name, source_medium, Lp_Query,
            sessions, pageviews, leads, bounce_rate, avg_session_duration, new_users
        ])
    
    # Create DataFrame from the list of rows
    df = pd.DataFrame(rows, columns=[
        'Date', 'Page Path', 'Session Source', 'Search Term', 'Campaign Name', 'Source/Medium', "Lp_Query",
        'Sessions', 'Pageviews', 'Leads', 'Bounce Rate', 'Avg. Session Duration', 'New Users'
    ])
    
    # Process date columns for easier handling
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by='Date', inplace=True)

    return df
