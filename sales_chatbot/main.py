import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Use environment variable for API URL, fallback to localhost for development
API_URL = os.getenv('API_URL', 'http://localhost:8000')

st.set_page_config(page_title="Sales Inventory Chatbot", page_icon=":speech_balloon:")

st.title("Sales Inventory Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "content": "Hello! I'm your Sales Inventory assistant. Ask me anything about your database!"},
    ]

with st.sidebar:
    st.subheader("Settings")
    st.write("Connect to your sales_inventory database and start chatting.")
    if st.button("Connect"):
        st.session_state.connected = True
        st.success("Connected to sales_inventory!")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = st.chat_input("Type a message...")
if user_query and st.session_state.get("connected", False):
    st.session_state.chat_history.append({"role": "human", "content": user_query})
    with st.chat_message("human"):
        st.markdown(user_query)
    with st.chat_message("ai"):
        try:
            # Make API call to backend
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "message": user_query,
                    "chat_history": st.session_state.chat_history
                }
            )
            response.raise_for_status()
            ai_response = response.json()["response"]
            st.markdown(ai_response)
            st.session_state.chat_history.append({"role": "ai", "content": ai_response})
        except Exception as e:
            st.error(f"Error: {str(e)}")
elif user_query and not st.session_state.get("connected", False):
    st.error("Please connect to the database first!")