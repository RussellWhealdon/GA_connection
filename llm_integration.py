import openai
import streamlit as st

# Function to load and query the LLM
def load_model():
    openai.api_key = st.secrets["openai"]["api_key"]

# Business context for the LLM - Define once at the start of the session
business_context = """
The business is currently focused on digital growth, improving conversion rates, and optimizing user acquisition channels.
Primary goals include increasing lead generation, enhancing engagement on the site, and understanding user search behavior for better SEO strategies.
Growth opportunities include expansion of content offerings, targeting high-conversion demographics, and improving the overall user experience.
"""

# Function to initialize the LLM session with business context
def initialize_llm_context():
    # Store the initial business context in the session state for continuity
    if "session_summary" not in st.session_state:
        st.session_state["session_summary"] = business_context

# Document Assist function for additional context - keeps it flexible for future RAG approach
def load_document_assist():
    # Example: Replace with actual document data or summaries as needed
    documents = {
        "SEO": "Search Engine Optimization strategies focusing on high-value keywords...",
        "User Acquisition": "User acquisition data by channel...",
        "Conversion Optimization": "Strategies to increase conversion rates for specific demographics...",
        # Add more document topics and summaries as needed
    }
    return documents

def query_gpt(prompt, document_context="", use_documents=False):
    try:
        # Retrieve session summary and document assist context
        session_summary = st.session_state.get("session_summary", "")
        
        # Combine the prompt with session memory and optional document assist
        full_prompt = f"{session_summary}\n\nAdditional Context:\n{document_context}\n\nUser Question: {prompt}"
        
        if use_documents:
            documents = load_document_assist()
            doc_context = "\n".join([f"{title}: {content}" for title, content in documents.items()])
            full_prompt += f"\n\nDocument References:\n{doc_context}"

        # Send the full prompt to GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst with a focus on digital growth and conversion optimization."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        # Extract the model's response and update session summary
        answer = response['choices'][0]['message']['content']
        st.session_state["session_summary"] += f"\nUser: {prompt}\nModel: {answer}\n"  # Update memory
        
        return answer


    except Exception as e:
        return f"Error: {e}"
