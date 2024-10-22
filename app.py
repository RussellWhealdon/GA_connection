import streamlit as st
import json
import logging
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest

# Configure logging to help debug
logging.basicConfig(level=logging.DEBUG)

# Function to fetch GA4 data
def run_ga4_report(property_id, credentials):
    try:
        # Initialize the client with credentials
        client = BetaAnalyticsDataClient(credentials=credentials)

        # Define the report request
        request = RunReportRequest(
            property=f"properties/{429942025}",  # GA4 Property ID
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews")]
        )

        # Run the report
        response = client.run_report(request=request)
        return response
    except Exception as e:
        logging.error(f"Error in run_ga4_report: {str(e)}")
        raise e

# Set up credentials
def load_credentials():
    try:
        # Load the credentials from the Streamlit secrets
        service_account_info = st.secrets["google_service_account"]
        
        # Create credentials from the service account info
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        logging.info("Successfully loaded credentials.")
        return credentials
    except Exception as e:
        logging.error(f"Error loading credentials: {str(e)}")
        st.error(f"Error loading credentials: {str(e)}")
        raise e

# Streamlit UI
def main():
    st.title("Google Analytics Data App")
    st.write("This app pulls d
