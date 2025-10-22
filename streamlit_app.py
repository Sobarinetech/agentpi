import streamlit as st
import requests

st.set_page_config(page_title="AgentPi Chat", page_icon="💬", layout="centered")

st.title("💬 AgentPi Chat Interface")

# Load credentials from st.secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]
API_ID = st.secrets["API_ID"]

# Streamlit input fields
st.subheader("Chat with AgentPi")

message = st.text_area("Enter your message:", placeholder="Type your message here...")
conversation_id = st.text_input("Conversation ID (optional):", "")

if st.button("Send Message"):
    if not message.strip():
        st.warning("Please enter a message before sending.")
    else:
        with st.spinner("Sending request..."):
            url = f"{SUPABASE_URL}/functions/v1/agentpi-chat"
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            }
            payload = {
                "message": message,
                "apiId": API_ID,
            }

            if conversation_id:
                payload["conversationId"] = conversation_id

            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                st.success("Response received!")
                st.markdown("### 🧠 Agent Response:")
                st.write(data.get("response", "No response field found."))

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
            except ValueError:
                st.error("Invalid JSON response from server.")
