import streamlit as st
import requests
from supabase import create_client, Client

# --- Streamlit Page Config ---
st.set_page_config(page_title="AgentPI Chat", page_icon="🤖", layout="centered")

st.title("🤖 AgentPI Chat Interface")
st.caption("Chat securely with your Supabase Edge Function (agentpi-chat)")

# --- Load Supabase Credentials ---
try:
    supabase_url = st.secrets["supabase"]["url"]
    supabase_anon_key = st.secrets["supabase"]["anon_key"]
except KeyError:
    st.error("Missing Supabase configuration in `.streamlit/secrets.toml`.")
    st.stop()

# --- Initialize Supabase Client ---
supabase: Client = create_client(supabase_url, supabase_anon_key)

# --- Session State for Auth ---
if "session" not in st.session_state:
    st.session_state.session = None


# --- Supabase Login ---
def login(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.session = res.session
        st.success(f"Logged in as {email}")
    except Exception as e:
        st.error(f"Login failed: {e}")


def logout():
    st.session_state.session = None
    st.success("Logged out successfully.")


# --- Authentication Section ---
if st.session_state.session is None:
    st.subheader("🔐 Login to Supabase")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(email, password)
    st.stop()

else:
    user = st.session_state.session.user
    st.sidebar.success(f"Logged in as: {user.email}")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()


# --- AgentPI Chat Function ---
def call_agentpi_chat(message: str, api_name: str):
    """
    Calls the Supabase Edge Function `agentpi-chat`
    with the user's message and API name.
    """
    endpoint = f"{supabase_url}/functions/v1/agentpi-chat"

    access_token = st.session_state.session.access_token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    body = {
        "messages": [{"role": "user", "content": message}],
        "apiName": api_name
    }

    try:
        with st.spinner("🤖 Waiting for AgentPI..."):
            response = requests.post(endpoint, json=body, headers=headers)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        try:
            detail = e.response.json()
            st.error(f"API Error: {detail.get('error', str(e))}")
        except Exception:
            st.error(f"Request failed: {e}")
        return None


# --- User Interface ---
st.subheader("💬 Chat with AgentPI")

with st.form("chat_form"):
    api_name = st.text_input("API Name", "extract-pdf")
    message = st.text_area(
        "Your Message",
        "Call the extract-pdf API with URL: https://example.com/document.pdf",
        height=100
    )
    submitted = st.form_submit_button("Send to AgentPI")

if submitted:
    if not message.strip():
        st.warning("Please enter a message before sending.")
    elif not api_name.strip():
        st.warning("Please provide the API name.")
    else:
        st.write("---")
        st.subheader("🧠 AgentPI Response")

        data = call_agentpi_chat(message, api_name)
        if data:
            st.json(data)


# --- Help Section ---
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    **Steps:**
    1. Log in using your Supabase email and password.
    2. Enter the API name (e.g., `extract-pdf`).
    3. Type a message describing the task you want to perform.
    4. The app securely calls your Supabase Edge Function (`agentpi-chat`).
    5. AgentPI responds with results based on your configured API.
    """)

