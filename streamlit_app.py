import streamlit as st
import requests

st.set_page_config(page_title="Hush API Chat", page_icon="🕵️", layout="centered")

# --- Load secrets from Streamlit Cloud or .streamlit/secrets.toml ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
AUTH_TOKEN = st.secrets["AUTH_TOKEN"]

# --- Setup ---
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
}

# --- Initialize conversation state ---
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

st.title("🕵️ Hush API Chat")
st.caption("Interact with your Supabase Edge Function")

# --- Input form ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("Enter your message", height=100, placeholder="Type something like: Use Flask to extract this PDF...")
    submitted = st.form_submit_button("Send")

# --- Function to send message ---
def send_message(msg):
    data = {
        "message": msg,
        "conversationHistory": st.session_state.conversation_history,
    }

    try:
        response = requests.post(SUPABASE_URL, json=data, headers=headers)
        result = response.json()

        if "response" in result:
            # Append to session state
            st.session_state.conversation_history.append({"role": "assistant", "content": result["response"]})
            return result["response"]
        else:
            return f"❌ Error: {result}"
    except Exception as e:
        return f"⚠️ Request failed: {e}"

# --- Handle message send ---
if submitted and user_input.strip():
    st.session_state.chat_log.append(("You", user_input))
    reply = send_message(user_input)
    st.session_state.chat_log.append(("Hush", reply))

# --- Display chat log ---
for sender, msg in st.session_state.chat_log:
    if sender == "You":
        st.markdown(f"🧑 **{sender}:** {msg}")
    else:
        st.markdown(f"🤖 **{sender}:** {msg}")

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
st.sidebar.write("Supabase Edge Function URL:")
st.sidebar.code(SUPABASE_URL)
st.sidebar.write("Auth token is securely loaded from `st.secrets`.")

st.sidebar.divider()
if st.sidebar.button("🧹 Clear Conversation"):
    st.session_state.conversation_history = []
    st.session_state.chat_log = []
    st.success("Conversation cleared!")
