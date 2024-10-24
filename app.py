import openai
import streamlit as st
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

# Load the secrets for the service account path and property ID
service_account_info = st.secrets["google_service_account"]  # Load service account JSON from secrets
property_id = st.secrets["google_service_account"]["property_id"]

# Initialize GA Client using the service account JSON
client = BetaAnalyticsDataClient.from_service_account_info(service_account_info)

# Function to fetch Google Analytics data with channel breakdowns
def get_ga_summary_data():
# Create a request with multiple metrics and 'date' as a dimension
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],  # Add 'date' as a dimension
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),         # Add more metrics as needed
            Metric(name="bounceRate")
        ],
        date_ranges=[DateRange(start_date="2024-09-01", end_date="2024-09-30")],
    )
    
    response = client.run_report(request)
    rows = []
    # Loop through the rows and extract date, activeUsers, sessions, and bounceRate
    for row in response.rows:
        # Extract values using dot notation
            date = row.dimension_values[0].value  # Extract the date
            active_users = row.metric_values[0].value  # Extract activeUsers
            sessions = row.metric_values[1].value  # Extract sessions
            bounce_rate = row.metric_values[2].value  # Extract bounceRate

            # Append row data to the list
            rows.append([date, active_users, sessions, bounce_rate])
    
    # Create a DataFrame with appropriate column names
    df = pd.DataFrame(rows, columns=['Date', 'Active Users', 'Sessions', 'Bounce Rate'])

    return ga_data

st.title("Google Analytics Data Analysis with GPT-4")
st.write("Google Analytics Data:")

# Fetch and display Google Analytics data
ga_data = get_ga_summary_data()

st.dataframe(ga_data)

# Function to query GPT-4 with data context
def query_gpt4(prompt, data):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": f"Here is some Google Analytics data:\n\n{data}\n\n{prompt}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Let the user ask GPT-4 a question
user_prompt = st.text_input("Ask GPT-4 something about this data:")

# If the user provides a prompt, analyze it
if user_prompt:
    data_summary = ga_data.head().to_csv(index=False)  # Summarize the data for GPT-4
    st.write("GPT-4 is analyzing the data...")
    response = query_gpt4(user_prompt, data_summary)
    st.write(response)
