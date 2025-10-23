import streamlit as st
import requests
import json

# ----------------------------
# CONFIGURATION
# ----------------------------
st.set_page_config(
    page_title="AgentPI Dashboard",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AgentPI – AI API Orchestrator")

# Load your Supabase project info
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"  # Replace with your project URL
SUPABASE_FUNCTION = f"{SUPABASE_URL}/functions/v1/agentpi-api"

# You can load from st.secrets in production
USER_TOKEN = st.secrets.get("supabase", {}).get("user_token", "")
API_KEY = st.secrets.get("supabase", {}).get("apikey", "")

if not USER_TOKEN or not API_KEY:
    st.warning("⚠️ Missing credentials. Add them to your Streamlit secrets.toml.")
    st.stop()

# ----------------------------
# SIDEBAR CONFIG
# ----------------------------
st.sidebar.header("🔧 Configuration")

api_id = st.sidebar.text_input("API ID", value="your-api-id")
api_name = st.sidebar.text_input("API Name (optional)")
message = st.text_area("💬 Message", "Fetch all active users")

if st.button("🚀 Run AI Agent"):
    with st.spinner("Processing your request..."):
        url = SUPABASE_FUNCTION
        headers = {
            "Authorization": f"Bearer {USER_TOKEN}",
            "apikey": API_KEY,
            "Content-Type": "application/json",
        }

        payload = {
            "apiId": api_id if api_id else None,
            "apiName": api_name if api_name else None,
            "messages": [
                {"role": "user", "content": message}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for 4xx/5xx

            result = response.json()
            if result.get("success"):
                st.success("✅ AI Response Received")

                st.subheader("🧠 AI Response")
                st.write(result["data"]["response"])

                st.subheader("📡 API Call Summary")
                api_calls = result["data"].get("apiCalls", [])
                if api_calls:
                    for call in api_calls:
                        st.json(call)
                else:
                    st.info("No API calls were made by the AI agent.")

                st.subheader("ℹ️ Metadata")
                st.json(result.get("metadata", {}))

            else:
                st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
                st.json(result)

        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection Error: Could not reach Supabase Edge Function.")
        except requests.exceptions.Timeout:
            st.error("⏳ Timeout Error: The request took too long.")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.caption("Powered by Supabase Edge Functions + Gemini + Streamlit 💡")
