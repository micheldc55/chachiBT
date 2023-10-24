import json
import os

import streamlit as st
import openai
from dotenv import load_dotenv

from src.llms.openai_models import OpenAiChatWithRetries
from src.messages.messages import Message, MessageHistory
from src.file_parsers.output_parsers import openai_response_parser
from src.utils.random_ids import generate_date_key_combination, load_conversation_ids, read_history_from_id


load_dotenv()

# Set your OpenAI API key here
openai.api_key = os.environ.get("OPENAI_KEY")

system_message = "You are a helpful assistant specialized in responding questions related to code."

st.header("ChatGPT")

col1, col2, col3 = st.columns([2, 2, 4])

model = col1.selectbox(label="Select your model:", options=["gpt-4", "gpt-3.5-turbo-0613"])
temperature = col2.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.2)

conversation_ids = load_conversation_ids()
selected_id = st.sidebar.selectbox('Choose a Conversation', conversation_ids)

new_conv = st.sidebar.button("Start a new conversation", key="restart_button")

if new_conv:
    st.session_state.restart = True

if ("restart" not in st.session_state) or st.session_state.restart == True:
    unique_id = generate_date_key_combination()
    st.session_state.unique_id = unique_id
    st.session_state.messages = MessageHistory()
    sys_msg_obj = Message("system", system_message)
    st.session_state.messages.add_message(sys_msg_obj)

    st.session_state.last_message = None

    st.session_state.restart = False

    st.session_state.messages.save_to_file(st.session_state.unique_id)

    st.rerun()

elif st.session_state.restart == False:
    unique_id = "data/conversations/" + selected_id + ".json"
    st.session_state.unique_id = unique_id
    st.session_state.messages = read_history_from_id(unique_id)


# Show chat
for message in st.session_state.messages.to_list():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What is up?")

if prompt is not None:
    new_message = Message(role="user", message=prompt)
    st.session_state.messages.add_message(new_message) 

    chat = OpenAiChatWithRetries(
        history=st.session_state.messages, 
        model=model,
        temperature=temperature
    )
    print("Made a call to OPENAI")
    response = chat(prompt)

    text_response, token_dict = openai_response_parser(response)
    assistant_message = Message("assistant", message=text_response)

    st.session_state.messages.add_message(assistant_message)

    st.session_state.messages.save_to_file(st.session_state.unique_id)

    st.session_state.last_message = prompt

    st.rerun()