import streamlit as st
from urllib.parse import unquote
import gsc_data_pull 

# Retrieve message from URL parameter
query_params = st.experimental_get_query_params()
message = query_params.get("message", ["No message received"])[0]

st.title("SEO Helper")
st.write("This is the SEO helper app.")
st.write("Message from Main App:", message)


def main():
    # Pull the same dataframe as in the main app
    df = gsc_data_pull.pull_data()  # Replace 'pull_data' with the actual function name
    
    # Retrieve and decode the response from URL parameter
    query_params = st.experimental_get_query_params()
    encoded_response = query_params.get("response", [""])[0]
    chatgpt_response = unquote(encoded_response)

    # Display SEO helper app
    st.title("SEO Helper")
    st.write("This is the SEO helper app.")
    
    # Display the dataframe
    st.write("GSC Data:", df)
    
    # Display the ChatGPT response
    st.write("ChatGPT SEO Response:", chatgpt_response)

# if __name__ == "__main__":
#     main()
