import openai
import streamlit as st
import pandas as pd
from ga4_data_pull import fetch_ga4_extended_data  # Import the new data pull function

# Load the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Set page configuration
st.set_page_config(
    page_title="Enhanced Google Analytics Data Dashboard",
    layout="wide",  # Enable the wide layout
)

# Initialize OpenAI client
gpt_client = openai.OpenAI(api_key=openai.api_key)

# Function to create summary for new GA4 data
def create_ga_extended_summary(df):
    # Ensure that numeric columns are truly numeric
    numeric_columns = ['Sessions', 'Pageviews', 'Leads', 'Avg. Session Duration', 'Bounce Rate', 'New Users']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Coerce errors to NaN

    # Convert 'Date' column to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])  # Keep as datetime for .dt access

    # Summarize main metrics
    total_sessions = df['Sessions'].sum()
    total_pageviews = df['Pageviews'].sum()
    total_leads = df['Leads'].sum()
    avg_bounce_rate = df['Bounce Rate'].mean()
    avg_session_duration = (df['Avg. Session Duration'].sum() / total_sessions) / 60  # Convert from seconds to minutes
    total_new_users = df['New Users'].sum()

    # Calculate top entries for insights
    top_page = df.groupby('Page Path')['Pageviews'].sum().idxmax()
    top_search_term = df.groupby('Search Term')['Sessions'].sum().idxmax()
    top_campaign = df.groupby('Campaign Name')['Leads'].sum().idxmax()
    top_source = df.groupby('Source/Medium')['Sessions'].sum().idxmax()

    # Construct the summary string
    summary = (
        f"Extended Website Performance Overview:\n\n"
        f"Total Sessions: {total_sessions}\n"
        f"Total Pageviews: {total_pageviews}\n"
        f"Total Leads: {total_leads}\n"
        f"Average Bounce Rate: {avg_bounce_rate:.2f}%\n"
        f"Average Session Duration: {avg_session_duration:.2f} minutes\n"
        f"Total New Users: {total_new_users}\n\n"
        f"Top Page by Pageviews: {top_page}\n"
        f"Top Search Term by Sessions: {top_search_term}\n"
        f"Top Campaign by Leads: {top_campaign}\n"
        f"Top Traffic Source: {top_source}\n"
    )

    return summary

def query_gpt4(prompt, data_summary):
    try:
        # Combine the user prompt with the GA summary
        full_prompt = f"Here is the extended website performance summary:\n\n{data_summary}\n\n{prompt}"

        # Send the combined prompt to GPT-4
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

st.title("Enhanced Google Analytics Data Analysis with GPT-4")
st.write("Google Analytics Data:")

# Fetch and display the enhanced Google Analytics data
ga_data = fetch_ga4_extended_data()
st.dataframe(ga_data)

# Generate the performance summary using the enhanced data
ga_summary = create_ga_extended_summary(ga_data)

with st.expander("See Performance Summary given to ChatGPT"):
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
