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
        dimensions=[
            Dimension(name="date"),                     # Break down by date
            Dimension(name="city"),                     # Break down by city
            Dimension(name="firstUserPrimaryChannelGroup"),  # Source/Medium
            Dimension(name="deviceCategory"),           # Break down by device category (desktop, mobile, tablet)
            Dimension(name="country"),                  # Break down by country
            Dimension(name="landingPagePlusQueryString")  # Break down by landing page
        ],
        metrics=[
            Metric(name="sessions"),                    # Total sessions
            Metric(name="activeUsers"),                 # Total active users
            Metric(name="screenPageViews"),             # Total pageviews
            Metric(name="uniquePageviews"),             # Unique pageviews
            Metric(name="bounceRate"),                  # Bounce rate
            Metric(name="averageSessionDuration"),      # Average session duration
            Metric(name="newUsers"),                    # New users
            Metric(name="transactions"),                # Transactions (for e-commerce)
            Metric(name="totalRevenue")                 # Revenue (for e-commerce)
        ],
        date_ranges=[DateRange(start_date="2024-09-01", end_date="2024-09-30")],  # Last month
    )
    
    response = client.run_report(request)
    rows = []
    # Loop through the rows and extract all dimensions and metrics
    for row in response.rows:
        # Extract dimension values using dot notation
        date = row.dimension_values[0].value  # Extract the date
        city = row.dimension_values[1].value  # Extract the city
        channel = row.dimension_values[2].value  # Extract the traffic source
        device = row.dimension_values[3].value  # Extract the device category
        country = row.dimension_values[4].value  # Extract the country
        landing_page = row.dimension_values[5].value  # Extract the landing page
    
        # Extract metric values using dot notation
        sessions = row.metric_values[0].value  # Extract sessions
        active_users = row.metric_values[1].value  # Extract active users
        pageviews = row.metric_values[2].value  # Extract pageviews
        unique_pageviews = row.metric_values[3].value  # Extract unique pageviews
        bounce_rate = row.metric_values[4].value  # Extract bounce rate
        avg_session_duration = row.metric_values[5].value  # Extract average session duration
        new_users = row.metric_values[6].value  # Extract new users
        transactions = row.metric_values[7].value  # Extract transactions
        revenue = row.metric_values[8].value  # Extract total revenue
    
        # Append all the extracted data to the list
        rows.append([
            date, city, channel, device, country, landing_page, sessions,
            active_users, pageviews, unique_pageviews, bounce_rate,
            avg_session_duration, new_users, transactions, revenue
        ])
    
    # Create a DataFrame with the appropriate column names
    df = pd.DataFrame(rows, columns=[
        'Date', 'City', 'Channel', 'Device', 'Country', 'Landing Page', 
        'Sessions', 'Active Users', 'Pageviews', 'Unique Pageviews', 
        'Bounce Rate', 'Avg. Session Duration', 'New Users', 
        'Transactions', 'Revenue'
    ])

    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date

    return df


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
