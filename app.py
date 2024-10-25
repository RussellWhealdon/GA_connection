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
            Metric(name="bounceRate"),                  # Bounce rate
            Metric(name="averageSessionDuration"),      # Average session duration
            Metric(name="newUsers"),                    # New users
        ],
        date_ranges=[DateRange(start_date="2024-09-01", end_date="2024-10-25")],  # Last month - Present
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
        bounce_rate = row.metric_values[3].value  # Extract bounce rate
        avg_session_duration = row.metric_values[4].value  # Extract average session duration
        new_users = row.metric_values[5].value  # Extract new users
    
        # Append all the extracted data to the list
        rows.append([
            date, city, channel, device, country, landing_page, sessions,
            active_users, pageviews, bounce_rate,
            avg_session_duration, new_users
        ])
    
    # Create a DataFrame with the appropriate column names
    df = pd.DataFrame(rows, columns=[
        'Date', 'City', 'Channel', 'Device', 'Country', 'Landing Page', 
        'Sessions', 'Active Users', 'Pageviews', 
        'Bounce Rate', 'Avg. Session Duration', 'New Users'
    ])

    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.date

    df.sort_values(by = ['Date'], inplace =True)
    return df

def convert_duration_to_seconds(duration):
    # Convert 'H:MM:SS' or 'MM:SS' format to total seconds
    try:
        time_parts = list(map(int, duration.split(":")))
        if len(time_parts) == 3:  # Format: HH:MM:SS
            return time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
        elif len(time_parts) == 2:  # Format: MM:SS
            return time_parts[0] * 60 + time_parts[1]
    except Exception:
        return 0  # If conversion fails, return 0

def convert_rate_to_float(rate):
    try:
        # Remove "%" symbol and convert to float
        return float(rate.strip('%')) / 100
    except Exception:
        return None  # Return None for invalid data

def create_ga_summary(df):
    # Ensure that numeric columns are truly numeric
    numeric_columns = ['Sessions', 'Active Users', 'New Users', 'Avg. Session Duration', 'Bounce Rate']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Coerce errors to NaN

    
    # Convert 'Avg. Session Duration' from time format to seconds
    #df['Avg. Session Duration'] = df['Avg. Session Duration'].apply(convert_duration_to_seconds)

    # Convert 'Bounce Rate' and other rate-based metrics to floats
    #df['Bounce Rate'] = df['Bounce Rate'].apply(convert_rate_to_float)
    
    # Extract necessary insights from the DataFrame
    total_sessions = df['Sessions'].sum()
    total_duration = df['Avg. Session Duration'].sum()
    avg_session_duration = (total_duration / total_sessions) / 60  # Convert from seconds to minutes
    bounce_rate = df['Bounce Rate'].mean()
    total_active_users = df['Active Users'].sum()
    new_users = df['New Users'].sum()
    top_channel = df.groupby('Channel')['Sessions'].sum().idxmax()  # Get the channel with most sessions
    top_city = df.groupby('City')['Sessions'].sum().idxmax()  # Get the city with most sessions
    top_device = df.groupby('Device')['Sessions'].sum().idxmax()  # Get the device with most sessions

    # Construct summary string
    summary = (
        f"Website Performance Overview:\n\n"
        f"1. Total Sessions: {total_sessions}\n"
        f"2. Active Users: {total_active_users}\n"
        f"3. New Users: {new_users}\n"
        f"4. Average Session Duration: {avg_session_duration:.2f} minutes\n"
        f"5. Bounce Rate: {bounce_rate:.2f}%\n"
        f"6. Top Traffic Channel: {top_channel}\n"
        f"7. Top City: {top_city}\n"
        f"8. Top Device: {top_device}\n"
    )

    return summary


# Load the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Initialize OpenAI client
gpt_client = openai.OpenAI(api_key=openai.api_key)



def query_gpt4(prompt, data_summary):
    try:
        # Combine the user prompt with the GA summary
        full_prompt = f"Here is the website performance summary:\n\n{data_summary}\n\n{prompt}"

        # Send the combined prompt to GPT-4 using the 'messages' parameter for chat-based models
        response = gpt_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": full_prompt}
            ]
        )

        # Return the response from GPT-4
        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {str(e)}"

st.title("Google Analytics Data Analysis with GPT-4")
st.write("Google Analytics Data:")

# Fetch and display Google Analytics data
ga_data = get_ga_summary_data()

st.dataframe(ga_data)

# Generate the performance summary
ga_summary = create_ga_summary(ga_data)

# Show the generated summary
st.write("Generated Performance Summary:")
st.write(ga_summary)

# Let the user ask GPT-4 a question about the data
user_prompt = st.text_input("Ask GPT-4 something about this data:")

# If the user provides a prompt, analyze it using GPT-4
if user_prompt:
    st.write("GPT-4 is analyzing the data...")
    response = query_gpt4(user_prompt, ga_summary)
    st.write(response)
