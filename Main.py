import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

#streamlit run Main.py --server.enableCORS false --server.enableXsrfProtection false

def __main__():
    # Initialize session state to keep track of the Second Brain data load status
    if 'second_brain_loaded' not in st.session_state:
        st.session_state.second_brain_loaded = False

    # Sidebar for Second Brain URL input
    st.sidebar.header("Talk to a Second Brain")
    st.sidebar.markdown("""
How to use:
- Specify URL to a second brain
- Click Load
- Talk to the second brain...

**NOTE**: Chat history, and other data is cleared  when the page is refreshed.""")
    
    second_brain_url = st.sidebar.text_input("Second Brain URL:", placeholder="Enter URL in click Load button")
    if st.sidebar.button("Load"):
        load_second_brain(second_brain_url)
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []

    st.sidebar.markdown("""
**DATA PRIVACY**: The data is sent to OpenAI company for processing. Please do not include any sensitive data in the second brain and/or in the questions. By using this app, you agree to the [OpenAI Privacy Policy](https://beta.openai.com/docs/api-reference/privacy-policy).
""")

    # Main page chat control
    st.title("Talk to a Second Brain")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Talk to the second brain..."):

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.second_brain_loaded:
            with st.spinner("Thinking..."):
                response = talk_to_second_brain(prompt)
        else:
            response = "Please upload data to a second brain."

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def load_second_brain(url: str) -> str:
    data = fetch_text_from_url(url);
    print(len(data))
    st.session_state.messages.append({"role": "user", "content": f"Second Brain size: {len(data)}"})
    if(len(data) > 25000):
        st.sidebar.warning("Second Brain data is too large to load! Max is 25000 characters.")
    else:
        st.session_state.second_brain_data = data
        st.session_state.second_brain_loaded = True
        st.sidebar.success("Second Brain data loaded successfully!")

def fetch_text_from_url(url):
    # Check if the URL is likely a Google Docs link
    if "docs.google.com/document" in url:
        # Attempt to construct the export URL for plain text
        doc_id = url.split('/d/')[1].split('/')[0]
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        
        # Get the response from the export URL
        response = requests.get(export_url)
        if response.status_code == 200:
            return response.text
        else:
            return "Failed to fetch or parse Google Docs content."
    else:
        # Assume it's a regular webpage and proceed to scrape
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            
            # Get text and clean up whitespace
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        else:
            return "Failed to fetch or parse webpage content."
        
def talk_to_second_brain(question) -> str:
    prompt = hub.pull("adjreality/sb_generic")
    chain = prompt | ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3) | StrOutputParser()
    return chain.invoke({ 
        "second_brain_data": st.session_state.second_brain_data, 
        "question": question
    })

__main__()
