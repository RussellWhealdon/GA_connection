import streamlit as st
from urllib.parse import unquote
import gsc_data_pull 
import requests
from bs4 import BeautifulSoup


def fetch_page_copy(url):
    try:
        # Fetch the content of the page
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful

        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title tag
        title = soup.title.string if soup.title else "No title found"

        # Extract the meta description
        meta_description = ""
        description_tag = soup.find("meta", attrs={"name": "description"})
        if description_tag and description_tag.get("content"):
            meta_description = description_tag["content"]
        else:
            meta_description = "No meta description found"

        # Extract meta keywords
        meta_keywords = ""
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and keywords_tag.get("content"):
            meta_keywords = keywords_tag["content"]
        else:
            meta_keywords = "No meta keywords found"

        # Extract main text from <p> and heading tags
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        page_text = "\n\n".join([para.get_text(strip=True) for para in paragraphs])

        # Combine all extracted data into a dictionary
        seo_data = {
            "Title": title,
            "Meta Description": meta_description,
            "Meta Keywords": meta_keywords,
            "Page Copy": page_text if page_text else "No main content found on this page."
        }

        return seo_data
    except requests.RequestException as e:
        return {"Error": f"An error occurred while fetching the page: {e}"}


def main():
    # Pull the same dataframe as in the main app
    df = gsc_data_pull.fetch_search_console_data()  # Replace 'pull_data' with the actual function name
    
    # Retrieve message from URL parameter
    query_params = st.experimental_get_query_params()
    message = query_params.get("message", ["No message received"])[0]

    # Display SEO helper app
    st.title("SEO Helper")
    st.write("This is the SEO helper app.")

    # Input field for the URL to scrape
    url = st.text_input("Enter a URL to scrape", placeholder="https://example.com")
    
    if url:
        st.write("Fetching content...")
        seo_data = fetch_page_copy(url)
        
        # Display SEO-relevant information
        st.subheader("SEO Information")
        st.write(f"**Title:** {seo_data['Title']}")
        st.write(f"**Meta Description:** {seo_data['Meta Description']}")
        st.write(f"**Meta Keywords:** {seo_data['Meta Keywords']}")
        st.subheader("Page Copy")
        st.write(seo_data["Page Copy"])

    # Display the dataframe
    #st.write("GSC Data:", df)
    
    # Display the ChatGPT response
    #st.write("ChatGPT SEO Response:", message)
 
if __name__ == "__main__":
     main()
