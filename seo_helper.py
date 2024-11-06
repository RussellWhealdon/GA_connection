import streamlit as st

# Retrieve message from URL parameter
query_params = st.experimental_get_query_params()
message = query_params.get("message", ["No message received"])[0]

st.title("SEO Helper")
st.write("This is the SEO helper app.")
st.write("Message from Main App:", message)
