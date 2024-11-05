from openai import OpenAI
import streamlit as st

# Initialize the OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Business context for session memory
business_context = """
The business is focused on digital growth, improving conversion rates, and optimizing user acquisition channels. 
Primary goals include increasing lead generation, enhancing engagement on the site, and understanding user search behavior for better SEO.
"""

# Mock function for testing prompts without API call
def query_gpt_test(prompt, data_summary=""):
    try:
        # Retrieve the session summary to include the business context and any prior conversation
        session_summary = st.session_state.get("session_summary", "")
        # Construct the full prompt for the final model interaction
        full_prompt = f"{session_summary}\n\nData Summary:\n{data_summary}\n\nUser Question: {prompt}"

        # Print the prompt to inspect it
        print("Final Prompt to GPT-4:")
        print(full_prompt)
        
        # Simulate a response without making an actual API call
        answer = "Mock response: Here’s how GPT-4 might respond based on this prompt."
        
        # Update the session memory with the simulated response
        st.session_state["session_summary"] += f"\nUser: {prompt}\nModel: {answer}\n"
        
        return answer

    except Exception as e:
        return f"Error: {e}"

# Test call
initialize_llm_context()  # Ensure the context is loaded
test_prompt = "What are some strategies for optimizing conversion rates?"
data_summary = "Conversion data shows higher engagement for organic traffic sources."

# Call the mock function instead of the actual API
response = query_gpt_test(test_prompt, data_summary)
print(response)


def initialize_llm_context():
    if "session_summary" not in st.session_state:
        st.session_state["session_summary"] = business_context

"""
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
"""
