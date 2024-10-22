import streamlit as st
import json
import logging
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest

# Configure logging to help debug
logging.basicConfig(level=logging.DEBUG)

# Function to fetch GA4 data
def run_ga4_report(property_id):
    try:
        # Initialize the client
        client = BetaAnalyticsDataClient()

        # Define the report request
        request = RunReportRequest(
            property=f"properties/{property_id}",  # GA4 Property ID
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
    st.write("This app pulls data from your Google Analytics account.")

    # Load credentials
    try:
        credentials = load_credentials()
    except Exception as e:
        return

    # Get the GA4 Property ID from secrets
    property_id = st.secrets["google_service_account"]["property_id"]

    # Fetch data from Google Analytics (GA4)
    try:
        logging.info("Fetching GA4 report...")
        response = run_ga4_report(property_id)

        if response:
            # Parse the response to extract useful information
            response_data = {
                "dimensions": [row.dimension_values for row in response.rows],
                "metrics": [row.metric_values for row in response.rows]
            }
            st.success("Data fetched successfully!")
            st.write("Response:", json.dumps(response_data, indent=2))
        else:
            st.error("No response received from GA4 API.")

    except Exception as e:
        logging.error(f"Failed to fetch data from Google Analytics: {str(e)}")
        st.error(f"Failed to fetch data from Google Analytics: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":
    main()
