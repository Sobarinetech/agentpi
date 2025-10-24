import streamlit as st
import requests
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="Hush API Chat", page_icon="🤖", layout="centered")

# --- APP HEADER ---
st.title("🤖 Hush API Chat")
st.caption("Streamlit app powered by Supabase Edge Function")

# --- LOAD CREDENTIALS FROM st.secrets ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_AUTH_TOKEN = st.secrets["SUPABASE_AUTH_TOKEN"]

# --- FUNCTION TO CALL SUPABASE EDGE FUNCTION ---
def call_hush_api(message, history):
    try:
        url = f"{SUPABASE_URL}/functions/v1/hush-api"
        headers = {
            "Authorization": f"Bearer {SUPABASE_AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {"message": message, "conversationHistory": history}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response field in API output.")
    except Exception as e:
        return f"❌ Error: {e}"

# --- STREAMLIT UI ---
st.write("Send a message to the Hush API below:")

# Store conversation history in session state
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_area("Your Message:", placeholder="Type something like: Extract data from this PDF ...")

if st.button("Send"):
    if user_input.strip():
        with st.spinner("Contacting Hush API..."):
            reply = call_hush_api(user_input, st.session_state.history)
            st.session_state.history.append({"role": "user", "content": user_input})
            st.session_state.history.append({"role": "assistant", "content": reply})
        st.success("✅ Response received!")
    else:
        st.warning("Please enter a message before sending.")

# --- DISPLAY CHAT HISTORY ---
st.subheader("🗨️ Conversation History")
for i, msg in enumerate(st.session_state.history):
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Hush API:** {msg['content']}")

