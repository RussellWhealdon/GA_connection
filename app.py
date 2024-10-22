import streamlit as st
import json
import os
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest

def run_ga4_report():
    # Initialize the client
    client = BetaAnalyticsDataClient()

    # Your GA4 property ID (replace with your property ID)
    property_id = "YOUR_GA4_PROPERTY_ID"

    # Define the report request
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")]
    )

    # Run the report
    response = client.run_report(request=request)

    return response


# Set up credentials
def load_credentials():
    # Load the credentials from the Streamlit secrets
    service_account_info = st.secrets["google_service_account"]
    
    # Create credentials from the service account info
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    
    return credentials

# Function to connect to GA4 API and fetch data
def get_analytics_data(credentials):
    # Build the Analytics Data API service
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    # Define the request body for the data you want to retrieve
    request_body = {
    'reportRequests': [{
        'viewId': '12345678',  # Replace this with your actual View ID
        'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
        'metrics': [{'expression': 'ga:pageviews'}],
        'dimensions': [{'name': 'ga:pagePath'}]
    }]
    }

    # Execute the request
    response = analytics.reports().batchGet(body=request_body).execute()
    return response

# Streamlit UI
def main():
    st.title("Google Analytics Data App")
    st.write("This app pulls data from your Google Analytics account.")

    # Load credentials
    credentials = load_credentials()

    # Fetch data from Google Analytics (GA4)
    with st.spinner("Fetching data..."):
        # Call the GA4 report function to fetch data
        response = run_ga4_report()

        # Parse the response to extract useful information
        # Here, we format the response for better readability
        if response:
            # Convert the response to a dictionary format
            response_data = {
                "dimensions": [row.dimension_values for row in response.rows],
                "metrics": [row.metric_values for row in response.rows]
            }
            st.success("Data fetched successfully!")
            st.write("Response:", json.dumps(response_data, indent=2))
        else:
            st.error("Failed to fetch data from Google Analytics.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
