import streamlit as st
import requests
from supabase import create_client, Client

st.set_page_config(page_title="AgentPi Chat", page_icon="💬", layout="centered")

st.title("💬 AgentPi Chat Interface")

# --- Load credentials from st.secrets ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
API_ID = st.secrets["API_ID"]

# --- Initialize Supabase client ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --- Authentication Section ---
st.subheader("🔐 Login to Supabase")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if "user" not in st.session_state:
    st.session_state.user = None

if st.button("Login"):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            st.session_state.user = res.user
            st.session_state.access_token = res.session.access_token
            st.success(f"Logged in as {res.user.email}")
        else:
            st.error("Login failed — check your credentials.")
    except Exception as e:
        st.error(f"Auth error: {e}")

if st.session_state.user:
    st.info(f"✅ Authenticated as {st.session_state.user.email}")
else:
    st.stop()  # stop here until user logs in

# --- Chat Interface ---
st.subheader("💬 Chat with AgentPi")

message = st.text_area("Enter your message:", placeholder="Type your message here...")
conversation_id = st.text_input("Conversation ID (optional):", "")

if st.button("Send Message"):
    if not message.strip():
        st.warning("Please enter a message before sending.")
    else:
        with st.spinner("Sending request..."):
            url = f"{SUPABASE_URL}/functions/v1/agentpi-chat"
            headers = {
                "Authorization": f"Bearer {st.session_state.access_token}",  # 👈 real user token
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
