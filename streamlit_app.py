import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="AgentPI API Runner",
    page_icon="⚙️",
    layout="centered",
)

# --- Header ---
st.title("⚙️ AgentPI API Runner")
st.caption("Interact securely with your Supabase Edge Function (`agentpi-api`).")

# --- Load Credentials ---
try:
    supabase_url = st.secrets["supabase"]["url"]
    user_token = st.secrets["supabase"]["access_token"]

    if not supabase_url or not user_token or "supabase.co" not in supabase_url:
        st.error("❌ Supabase credentials are not configured correctly in `st.secrets`.")
        st.info("Please create a `.streamlit/secrets.toml` file with your Supabase URL and Access Token.")
        st.stop()
except (KeyError, FileNotFoundError):
    st.error("❌ Secrets file not found or misconfigured.")
    st.info("Please create a `.streamlit/secrets.toml` file as per setup instructions.")
    st.stop()

# --- API Call Function ---
def call_agentpi_api(api_id: str, user_message: str):
    """
    Calls the agentpi-api edge function using credentials from st.secrets.
    """
    endpoint = f"{supabase_url}/functions/v1/agentpi-api"
    headers = {
        "Authorization": f"Bearer {user_token}",
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
            response = requests.post(endpoint, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

        if result.get("success"):
            st.success("✅ Request successful!")
            st.subheader("AI Response")
            st.write(result["data"].get("response", "No response field found."))

            st.subheader("📊 API Calls")
            st.json(result["data"].get("apiCalls", {}))
        else:
            st.error("⚠️ API Error")
            st.write(result.get("message", "Unknown error."))

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                st.error(f"Error details: {error_detail.get('error', 'No details provided.')}")
            except Exception:
                pass
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")

# --- User Interface ---
with st.form("agentpi_form"):
    api_id = st.text_input(
        "API ID",
        value="your-api-id",
        help="Enter the API ID configured in your AgentPI environment."
    )
    user_message = st.text_area(
        "User Message",
        value="Fetch all active users",
        height=120,
        help="Enter a natural language command to send to the AgentPI function."
    )
    submitted = st.form_submit_button("🚀 Run API Call")

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
    **Usage Steps:**
    1. 🔐 Configure your Supabase credentials in `.streamlit/secrets.toml`.
    2. 🧩 Enter your AgentPI `apiId` (from Supabase or your project config).
    3. 💬 Type a message or instruction (e.g., “Fetch all active users”).
    4. 🚀 Click **Run API Call** to send the request.
    5. 📦 View the structured JSON response below.
    
    ---
    **Security Note:**  
    Your credentials are securely loaded via `st.secrets` and never exposed in code or logs.
    """)

