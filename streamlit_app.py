import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="AgentPI Chat",
    page_icon="🤖",
    layout="centered",
)

# --- Title & Description ---
st.title("🤖 AgentPI Chat Interface")
st.caption("A Streamlit app to interact securely with the Supabase agentpi-chat function.")

# --- Load Credentials ---
try:
    supabase_url = st.secrets["supabase"]["url"]
    access_token = st.secrets["supabase"]["access_token"]

    if not supabase_url or not access_token or supabase_url == "YOUR_SUPABASE_URL":
        st.error("❌ Supabase credentials are not configured correctly in st.secrets.")
        st.info("Please create a `.streamlit/secrets.toml` file with your Supabase URL and Access Token.")
        st.stop()
except (KeyError, FileNotFoundError):
    st.error("❌ Secrets file not found or misconfigured.")
    st.info("Please create a `.streamlit/secrets.toml` file as per the setup guide.")
    st.stop()


# --- API Call Function ---
def call_agentpi_chat(message: str, api_name: str):
    """
    Calls the agentpi-chat edge function with the provided message and API name.
    """
    endpoint = f"{supabase_url}/functions/v1/agentpi-chat"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "messages": [{"role": "user", "content": message}],
        "apiName": api_name
    }

    try:
        with st.spinner("🤖 Waiting for AgentPI to respond..."):
            response = requests.post(endpoint, json=body, headers=headers)
            response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        # Show HTTP or connection error details
        st.error(f"⚠️ API Request Failed: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                st.error(f"Error details: {error_detail.get('error', 'No details provided.')}")
            except Exception:
                pass
        return None

    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


# --- User Input Form ---
with st.form("chat_form"):
    api_name_input = st.text_input(
        "API Name",
        value="extract-pdf",
        help="Enter the name of the AgentPI API to call (e.g., 'extract-pdf')."
    )
    user_message = st.text_area(
        "Your Message",
        value="Call the extract-pdf API with URL: https://example.com/document.pdf",
        height=120,
        help="Enter a natural language command for the AI agent."
    )
    submitted = st.form_submit_button("🚀 Send to AgentPI")

# --- Handle Submission ---
if submitted:
    if not user_message.strip():
        st.warning("Please enter a message before sending.")
    elif not api_name_input.strip():
        st.warning("Please enter an API name.")
    else:
        st.write("---")
        st.subheader("💬 AgentPI Response")

        api_response = call_agentpi_chat(user_message, api_name_input)

        if api_response:
            st.json(api_response)
        else:
            st.error("No response received from AgentPI.")


# --- Usage Instructions ---
with st.expander("ℹ️ How to use this app"):
    st.markdown("""
    **Steps:**
    1. 🧩 **Enter API Name:** Specify the AgentPI API you want to interact with (e.g., `extract-pdf`).
    2. 💬 **Enter Command:** Type a natural language instruction (e.g., “Extract text from this PDF...”).
    3. 🚀 **Send:** Click the *Send to AgentPI* button.
    4. 📦 **View Response:** The app securely calls your Supabase `agentpi-chat` function and displays the JSON response here.
    """)

    st.markdown("---")
    st.markdown("🔒 **Security Note:** Your credentials are loaded securely via `st.secrets` and never exposed in code or logs.")
