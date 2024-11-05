from openai import OpenAI
import streamlit as st

# Initialize the OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Business context for session memory
business_context = """
Answer these prompts with this context in mind. This data is coming from the website of a one person run dietitian who is somewhat technically versed. She started her 
website about a year ago and is tring to use data from GA4 to better its perfromance and grow her business. She needs help extracting useful insights from the data and 
making business deciscions from this. Keep all feedback simple and actionable, no unecessary business jargon. 
"""

def initialize_llm_context():
    if "session_summary" not in st.session_state:
        st.session_state["session_summary"] = business_context

def query_gpt(prompt, data_summary=""):
    try:
        session_summary = st.session_state.get("session_summary", "")
        full_prompt = f"{session_summary}\n\nData Summary:\n{data_summary}\n\nUser Question: {prompt}"

        # Send the prompt to GPT-4 through the OpenAI client instance
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst with a focus on digital growth and conversion optimization."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        # Access the response using dot notation
        answer = response.choices[0].message.content
        st.session_state["session_summary"] += f"\nUser: {prompt}\nModel: {answer}\n"
        
        return answer

    except Exception as e:
        return f"Error: {e}"
