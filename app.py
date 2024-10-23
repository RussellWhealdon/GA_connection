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
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="2023-01-01", end_date="2023-01-31")],
    )
    try:
        response = client.run_report(request)
        print(response)
    except Exception as e:
        print(f"Error: {e}")
    
    # Process response to a DataFrame
    rows = []
    for row in response.rows:
        rows.append({
            "date": row.dimension_values[0].value,
            "source": row.dimension_values[1].value,
            "sessions": row.metric_values[0].value,
            "activeUsers": row.metric_values[1].value,
            "bounceRate": row.metric_values[2].value
        })
    st.write(response.rows)
    return pd.DataFrame(rows)

def sample_run_report(property_id="YOUR-GA4-PROPERTY-ID"):
    """Runs a simple report on a Google Analytics 4 property."""

    # Initialize the BetaAnalyticsDataClient
    client = BetaAnalyticsDataClient()

    # Create the report request
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
    )

    # Run the report
    response = client.run_report(request)
    print(response)

    # Print the results
    print("Report result:")
    for row in response.rows:
        print(row.dimension_values[0].value, row.metric_values[0].value)

st.title("Google Analytics Data Analysis with GPT-4")
st.write("Google Analytics Data:")
sample_run_report(property_id)

# Fetch and display Google Analytics data
#ga_data = get_ga_summary_data()

#st.dataframe(ga_data)

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
