import streamlit as st
import json
import os
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
            'viewId': 'YOUR_VIEW_ID',  # Replace with your Google Analytics view ID
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

    # Fetch data from Google Analytics
    with st.spinner("Fetching data..."):
        data = get_analytics_data(credentials)
        st.success("Data fetched successfully!")

    # Display raw data or processed info
    st.write("Response:", json.dumps(data, indent=2))

# Run the Streamlit app
if __name__ == "__main__":
    main()
