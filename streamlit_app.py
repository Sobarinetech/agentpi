import streamlit as st
import requests

# Set page configuration
st.set_page_config(
    page_title="Hush API Interaction",
    layout="centered"
)

# --- Constants from the original script ---
API_URL = 'https://avdqcbeyygoeagrmcqcl.supabase.co/functions/v1/agent-api'
CONTENT_TYPE = 'application/json'

# --- Streamlit Title and Introduction ---
st.title("🤖 Hush API Chatbot")
st.markdown("Enter your message to interact with the Hush API. The API key is securely loaded from `st.secrets`.")

# --- API Key Retrieval ---
try:
    # Retrieve the authentication token from st.secrets
    AUTH_TOKEN = st.secrets["hush_api"]["auth_token"]
except (KeyError, AttributeError):
    st.error("🚨 API authentication token not found in `st.secrets`. Please configure `secrets.toml`.")
    st.stop() # Stop the app if the secret isn't available

# --- User Input ---
user_message = st.text_area(
    "Your Message:",
    placeholder="e.g., Use flask to extract this PDF: https://example.com/doc.pdf",
    height=150
)

# --- Function to Call API ---
@st.spinner("Sending message and awaiting response...")
def call_hush_api(message):
    """Sends the message to the Hush API and returns the response."""
    
    # Define headers using the retrieved token
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': CONTENT_TYPE
    }
    
    # Define the payload
    # Note: 'conversationHistory' is kept as an empty list as per the original script
    data = {
        'message': message,
        'conversationHistory': []
    }
    
    try:
        # Make the POST request
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()
        
        # Check if the expected 'response' key exists in the JSON result
        if 'response' in result:
            return result['response']
        else:
            return f"API call successful, but the expected 'response' key was missing. Full result: {result}"

    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: {e}. Status Code: {response.status_code}. Response: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred during the API request: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Submit Button and Output ---
if st.button("Send Message 🚀"):
    if user_message:
        # Call the API function
        api_response = call_hush_api(user_message)
        
        # Display the result
        st.subheader("API Response")
        st.info(api_response)
    else:
        st.warning("Please enter a message to send.")

# --- Optional: Display API URL for context ---
st.markdown("---")
st.caption(f"Target API: `{API_URL}`")
