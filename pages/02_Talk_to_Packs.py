import streamlit as st
import requests
import json

def __main__():
    # Sidebar for Second Brain URL input
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
How to use:
- Specify MnemoPack ID
- Communicate with it in the chat
                        
**NOTE**: Use <a href="/Manage_Packs/" target="_self">Manage Packs</a> to create a pack.
""", unsafe_allow_html=True)
    
    pack_id = st.sidebar.text_input("MenmoPack ID", key="pack_id")

    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []

    st.sidebar.markdown("""
[Privace Policy](https://docs.google.com/document/d/e/2PACX-1vTDIondyAvgPSy2bikCT2YEDw0S3FTfdECAbLAXouaYzvA5ig36MhlwW-sVyz6s2okoDr-vfAumjOap/pub)
""")

    # Main page chat control
    st.title("Talk to MnemoPack")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Talk to MnemoPack ...", disabled=False if pack_id else True):

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Communicating with the pack..."):
            if pack_id:
                response = talk_to_pack(pack_id, prompt)
                if response:
                    # Display assistant response in chat message container
                    with st.chat_message("assistant"):
                        st.markdown(response)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("Please specify the pack Id")


def talk_to_pack(pack_id, question) -> str:

    # URL of the API
    url = 'http://127.0.0.1:8100/talk/pack/invoke'

    # Sample input and config data
    input_data = {
        "input": {
            "pack_id": pack_id,
            "question": question
        },
        "config": {},  # Include necessary configuration details if any
        "kwargs": {}   # Include any additional keyword arguments if required
    }

    # Headers to indicate JSON content
    headers = {
        'Content-Type': 'application/json'
    }

    # Making a POST request
    response = requests.post(url, headers=headers, data=json.dumps(input_data))
    print("Response:", response.json())

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()["output"]
    else:
        print("Failed to make request.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

    return None


__main__()
