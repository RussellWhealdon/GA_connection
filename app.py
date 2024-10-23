import openai
import streamlit as st
import json
import logging
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Function to fetch GA4 data
def run_ga4_sessions_report(property_id, credentials):
    try:
        # Initialize the client with the explicit credentials
        client = BetaAnalyticsDataClient(credentials=credentials)

        # Define the report request to get 'sessions' metric for 'yesterday'
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date="2024-10-01", end_date="yesterday")],
            metrics=[Metric(name="sessions")],  # Fetch 'sessions' metric
        )

        # Run the report
        response = client.run_report(request=request)
        return response
    except Exception as e:
        logging.error(f"Error in run_ga4_sessions_report: {str(e)}")
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

def query_gpt4(prompt):
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=150  # You can adjust the number of tokens
    )
    return response.choices[0].text.strip()

st.title("GA Data Insights")
user_input = st.text_input("Ask a question about your GA data")

if user_input:
    response = query_gpt4(user_input)
    st.write(response)

# Streamlit UI
def main():
    st.title("Google Analytics Sessions Data App")
    st.write("This app pulls the number of sessions from yesterday.")

    # Load credentials
    credentials = load_credentials()
    
    # Get the GA4 Property ID from secrets
    property_id = st.secrets["google_service_account"]["property_id"]
    logging.info(f"Using property ID: {property_id}")

    # Fetch data from Google Analytics (GA4)
    try:
        logging.info("Fetching GA4 sessions report...")
        response = run_ga4_sessions_report(property_id, credentials)

        if response:
            # Parse the response to extract the number of sessions
            sessions = response.rows[0].metric_values[0].value
            st.success(f"Number of sessions this month: {sessions}")
        else:
            st.error("No response received from GA4 API.")
            logging.error("No response received from GA4 API.")

    except Exception as e:
        logging.error(f"Failed to fetch data from Google Analytics: {str(e)}")
        st.error(f"Failed to fetch data from Google Analytics: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":
    main()
