import streamlit as st
from chatbot.chatbot import system_prompt, stream_response
from langchain.schema import HumanMessage, AIMessage

st.set_page_config(page_title="SafarAI Learning Assistant", layout="wide")
st.title("📘 SafarAI Learning Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]  # only system prompt initially

# Display full chat history (excluding the system prompt)
for msg in st.session_state.messages[1:]:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Input box
user_input = st.chat_input("Ask me anything about English...")

if user_input:
    # Add user message to history
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get and display AI response
    with st.chat_message("assistant"):
        streamed_text = st.empty()  # Placeholder for streaming
        full_response = ""

        for chunk in stream_response(st.session_state.messages):
            if chunk.content:
                full_response += chunk.content
                streamed_text.markdown(full_response)

    st.session_state.messages.append(AIMessage(content=full_response))