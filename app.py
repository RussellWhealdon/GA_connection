import openai
import streamlit as st
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

# Load the secrets for the service account path and property ID
service_account_info = st.secrets["service_account_info"]  # Load service account JSON from secrets
property_id = st.secrets["google_service_account"]["property_id"]

# Initialize GA Client using the service account JSON
client = BetaAnalyticsDataClient.from_service_account_info(service_account_info)

# Function to fetch Google Analytics data
def get_ga_data():
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="2023-01-01", end_date="2023-12-31")],
        dimensions=[Dimension(name="pageTitle")],
        metrics=[Metric(name="activeUsers")],
    )
    response = client.run_report(request)
    
    # Process response to a DataFrame
    rows = []
    for row in response.rows:
        rows.append({
            "pageTitle": row.dimension_values[0].value,
            "activeUsers": row.metric_values[0].value
        })
    return pd.DataFrame(rows)

# Fetch and display Google Analytics data
ga_data = get_ga_data()

st.title("Google Analytics Data Analysis with GPT-4")
st.write("Google Analytics Data:")
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
