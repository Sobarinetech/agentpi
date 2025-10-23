import streamlit as st
import requests

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AgentPI API Runner",
    page_icon="🤖",
    layout="centered",
)

# --- App Header ---
st.title("🤖 AgentPI API Runner")
st.caption("Interact securely with your Supabase Edge Function (`agentpi-api`).")

# --- Load Secrets ---
try:
    supabase_url = st.secrets["supabase"]["url"]
    user_token = st.secrets["supabase"]["user_token"]

    if not supabase_url or not user_token or "supabase.co" not in supabase_url:
        st.error("❌ Supabase credentials are missing or misconfigured in `.streamlit/secrets.toml`.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error loading secrets: {e}")
    st.info("Please ensure `.streamlit/secrets.toml` exists and contains the required fields.")
    st.stop()

# --- Constants ---
SUPABASE_API_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlieWFrenh4eGlnYXhneWhtdXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNTU2NDIsImV4cCI6MjA3NjYzMTY0Mn0."
    "EnhWQjiEqEFxA0j6XxTdCbLFynRHvWxt0NfYo7AHaYo"
)

# --- Function to Call the API ---
def call_agentpi_api(api_id: str, user_message: str):
    url = f"{supabase_url}/functions/v1/agentpi-api"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "apikey": SUPABASE_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "apiId": api_id,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    try:
        with st.spinner("🔄 Contacting AgentPI API..."):
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

        if result.get("success"):
            st.success("✅ API call successful!")
            st.subheader("🧠 AI Response")
            st.write(result["data"].get("response", "No response field found."))

            st.subheader("📊 API Calls")
            st.json(result["data"].get("apiCalls", {}))
        else:
            st.error("⚠️ API returned an error:")
            st.write(result.get("message", "Unknown error."))

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {e}")
        if e.response is not None:
            try:
                st.json(e.response.json())
            except Exception:
                st.error("Failed to parse error response.")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")

# --- Streamlit Form for User Input ---
with st.form("agentpi_form"):
    api_id = st.text_input(
        "API ID",
        value="your-api-id",
        help="Enter the API ID you configured in Supabase AgentPI."
    )
    user_message = st.text_area(
        "Your Message",
        value="Fetch all active users",
        height=120,
        help="Enter a natural language instruction to send to the AgentPI function."
    )
    submitted = st.form_submit_button("🚀 Send to AgentPI")

if submitted:
    if not api_id.strip() or api_id == "your-api-id":
        st.warning("Please enter a valid API ID.")
    elif not user_message.strip():
        st.warning("Please enter a message.")
    else:
        call_agentpi_api(api_id, user_message)

# --- Instructions ---
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    **Steps to Use:**
    1. 🔐 Create a `.streamlit/secrets.toml` file with your Supabase URL and `user_token`.
    2. 🧩 Enter your AgentPI `apiId` (from your Supabase project setup).
    3. 💬 Enter a command or query (e.g., “Fetch all active users”).
    4. 🚀 Click **Send to AgentPI** to execute the request.
    5. 📦 View the AI’s response and any API calls below.
    
    ---
    **Security Tip:**  
    Your credentials are loaded via `st.secrets` and never stored or logged in plain text.
    """)
