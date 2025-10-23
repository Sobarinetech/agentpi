import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="AgentPI API Runner",
    page_icon="🤖",
    layout="centered",
)

# --- Header ---
st.title("🤖 AgentPI API Runner")
st.caption("Interact securely with your Supabase Edge Function (`agentpi-api`).")

# --- Load Credentials ---
try:
    supabase_url = st.secrets["supabase"]["url"].rstrip("/")  # remove trailing slash if any
    user_token = st.secrets["supabase"]["user_token"]
except Exception as e:
    st.error(f"⚠️ Error loading secrets: {e}")
    st.stop()

if not supabase_url.startswith("https://") or not user_token:
    st.error("❌ Invalid Supabase URL or user token.")
    st.stop()

# --- Constant API Key (from your example) ---
SUPABASE_API_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlieWFrenh4eGlnYXhneWhtdXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNTU2NDIsImV4cCI6MjA3NjYzMTY0Mn0."
    "EnhWQjiEqEFxA0j6XxTdCbLFynRHvWxt0NfYo7AHaYo"
)

# --- API Call Function ---
def call_agentpi_api(api_id: str, user_message: str):
    url = f"{supabase_url}/functions/v1/agentpi-api"  # ✅ correct endpoint
    headers = {
        "Authorization": f"Bearer {user_token}",
        "apikey": SUPABASE_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "apiId": api_id,
        "messages": [{"role": "user", "content": user_message}],
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

# --- Form UI ---
with st.form("agentpi_form"):
    api_id = st.text_input("API ID", "your-api-id")
    user_message = st.text_area("Your Message", "Fetch all active users", height=120)
    submitted = st.form_submit_button("🚀 Send to AgentPI")

if submitted:
    if not api_id.strip() or api_id == "your-api-id":
        st.warning("Please enter a valid API ID.")
    elif not user_message.strip():
        st.warning("Please enter a message.")
    else:
        call_agentpi_api(api_id, user_message)

# --- Help Section ---
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    **Setup:**
    1. Add your Supabase credentials in `.streamlit/secrets.toml`:
       ```toml
       [supabase]
       url = "https://<your-project>.supabase.co"
       user_token = "YOUR_TOKEN"
       ```
    2. Run:
       ```bash
       streamlit run app.py
       ```
    3. Enter your API ID and message, then click **Send**.
    """)
