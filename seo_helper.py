import streamlit as st
from urllib.parse import unquote
import gsc_data_pull 


def main():
    # Pull the same dataframe as in the main app
    df = gsc_data_pull.fetch_search_console_data()  # Replace 'pull_data' with the actual function name
    
    # Retrieve message from URL parameter
    query_params = st.experimental_get_query_params()
    message = query_params.get("message", ["No message received"])[0]

    # Display SEO helper app
    st.title("SEO Helper")
    st.write("This is the SEO helper app.")
    
    # Display the dataframe
    st.write("GSC Data:", df)
    
    # Display the ChatGPT response
    st.write("ChatGPT SEO Response:", message)
 
if __name__ == "__main__":
     main()
