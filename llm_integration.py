import openai
import streamlit as st

# Function to load and query the LLM
def load_model():
    openai.api_key = st.secrets["openai"]["api_key"]

def query_gpt(prompt, session_summary, document_context=""):
    try:
        # Combine session summary, document context, and user prompt
        full_prompt = f"{session_summary}\n\nAdditional Context:\n{document_context}\n\nUser Question: {prompt}"

        # Send the prompt to GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst with access to analytics summaries."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        # Extract and return the answer
        answer = response['choices'][0]['message']['content']
        return answer

    except Exception as e:
        return f"Error: {e}"
