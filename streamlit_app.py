import streamlit as st
import requests
import json
import time

# --- 1. Configuration and Constants ---
# Load configuration from st.secrets. Provide safe defaults for initial setup.
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", "your-anon-key")
# Assuming the function is named 'agentpi', adjust if yours is different.
EDGE_FUNCTION_URL = st.secrets.get("EDGE_FUNCTION_URL", f"{SUPABASE_URL}/functions/v1/agentpi") 

MAX_RETRIES = 3
INITIAL_BACKOFF = 1 # seconds

# --- 2. State Initialization ---
# Initialize session state for chat history and configuration inputs
if "messages" not in st.session_state:
    st.session_state.messages = []

if "auth_token" not in st.session_state:
    st.session_state.auth_token = ""

if "api_identifier" not in st.session_state:
    st.session_state.api_identifier = ""

# --- 3. Core Logic: Calling the Edge Function with Retries ---
def _call_edge_function(token, identifier, messages, is_id):
    """Calls the Supabase Edge Function with exponential backoff."""
    
    # 1. Prepare Request Payload
    payload = {
        "messages": messages
    }
    # Send either apiId or apiName based on user selection
    if is_id:
        payload["apiId"] = identifier
    else:
        payload["apiName"] = identifier

    # 2. Prepare Headers (Crucial: JWT is sent as Authorization header)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    st.toast(f"Sending request to Edge Function...")
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Send the POST request to the Edge Function
            response = requests.post(EDGE_FUNCTION_URL, headers=headers, data=json.dumps(payload), timeout=60)
            
            # Check for non-transient errors (4xx) which indicate configuration issues
            if 400 <= response.status_code < 500:
                # If we get a 401/403/404, stop retrying
                error_data = response.json() if response.content else {"error": response.text}
                st.error(f"Request failed (HTTP {response.status_code}): Check JWT/API Config.")
                return {"error": error_data.get("error", "Client/Config error."), "status": response.status_code}
            
            response.raise_for_status() # Raises HTTPError for 4xx or 5xx status codes
            
            # Successful response
            return response.json()
            
        except requests.exceptions.Timeout:
            retries += 1
            if retries < MAX_RETRIES:
                st.warning(f"Timeout on attempt {retries}. Retrying in {INITIAL_BACKOFF * (2 ** (retries - 1))}s...")
                time.sleep(INITIAL_BACKOFF * (2 ** (retries - 1)))
            else:
                st.error("Request timed out after multiple retries. Edge function may be too slow.")
                return {"error": "Request timed out after multiple retries."}
        
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries < MAX_RETRIES:
                st.warning(f"Request failed (Attempt {retries}): {e}. Retrying...")
                time.sleep(INITIAL_BACKOFF * (2 ** (retries - 1)))
            else:
                st.error(f"Request failed after multiple retries: {e}")
                return {"error": str(e)}

    return {"error": "Failed to get a response from the Edge Function."}

# --- 4. Streamlit UI and Chat Handler ---

st.set_page_config(page_title="AgentPI: Secure Gemini Tooling", layout="wide")

st.title("🤖 AgentPI: Secure Gemini Tooling via Supabase")
st.markdown(
    """
    Use this interface to chat with your customized AgentPI. It uses your Supabase JWT and API Identifier to securely 
    proxy requests to the Gemini API through your Edge Function, which applies RLS for API config access and executes 
    tool calls based on the LLM's instructions.
    """
)
st.divider()

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("1. Authentication & API Target")
    
    # JWT Input
    st.session_state.auth_token = st.text_input(
        "Supabase User JWT (Bearer Token)",
        value=st.session_state.auth_token,
        type="password",
        placeholder="Enter your valid Supabase JWT here...",
        help="This JWT is required for the Edge Function to authenticate your user and enforce RLS on the `api_configs` table."
    )

    # API Identifier Type Selection
    api_identifier_type = st.radio(
        "Target API Config By:", 
        ["ID (UUID)", "Name (String)"], 
        index=1, 
        help="Select how you're identifying your API configuration (from the `api_configs` table)."
    )
    is_id = api_identifier_type.startswith("ID")
    
    # API Identifier Input
    st.session_state.api_identifier = st.text_input(
        f"API Identifier ({'ID' if is_id else 'Name'})",
        value=st.session_state.api_identifier,
        placeholder="Enter API ID or Name...",
        help="The ID or Name of the API configuration you want AgentPI to use."
    )

    st.header("2. App Status")
    st.markdown(f"**Edge Function URL:** `{EDGE_FUNCTION_URL}`")
    st.info("Ensure the above URL and your secrets are configured correctly.")
    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.experimental_rerun()
        
# --- Main Chat Interface ---

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Use markdown to display content which includes line breaks and code blocks
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask AgentPI a question or command, e.g., 'What is the latest status using the API?'"):
    
    # 1. Validation
    if not st.session_state.auth_token or not st.session_state.api_identifier:
        st.error("🚨 Please provide a valid **JWT** and **API Identifier** in the sidebar to begin chatting.")
        # Do not append the message if validation fails
    else:
        # 2. Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 3. Call the Edge Function and display response
        with st.chat_message("assistant"):
            with st.spinner("AgentPI is connecting to the Edge Function and running the LLM/Tooling flow..."):
                
                # Format current messages for the API call (Edge Function expects simple role/content objects)
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state.messages
                ]
                
                # Get the response from the Edge Function
                response_data = _call_edge_function(
                    st.session_state.auth_token,
                    st.session_state.api_identifier,
                    api_messages,
                    is_id
                )
            
            # 4. Process and display response
            output_content = ""
            
            # Handle Errors from the Edge Function
            if "error" in response_data:
                full_error = f"**Edge Function Error (Status: {response_data.get('status', 'N/A')})**\n\n```json\n{json.dumps(response_data, indent=2)}\n```"
                output_content = full_error
                st.error(output_content)
            else:
                # Success
                llm_response = response_data.get("response", "AgentPI did not return a text response.")
                function_calls = response_data.get("functionCalls", [])
                
                output_content = llm_response
                
                # Optional: Show details of the executed API call
                if function_calls:
                    api_details_markdown = "\n\n---\n\n"
                    api_details_markdown += "**🛠️ API Call Details (Tool Execution):**\n\n"
                    for call in function_calls:
                        call_name = call.get("name", "tool")
                        call_response = call.get("response", {})
                        
                        api_details_markdown += f"- **Tool Name:** `{call_name}`\n"
                        api_details_markdown += f"- **Status:** `{call_response.get('status', 'N/A')}`\n"
                        
                        body_display = call_response.get('body', {})
                        if isinstance(body_display, str):
                            body_preview = body_display[:200] + "..." if len(body_display) > 200 else body_display
                            api_details_markdown += f"- **Response Body Preview:**\n```text\n{body_preview}\n```"
                        else:
                            body_preview = json.dumps(body_display, indent=2)
                            api_details_markdown += f"- **Response Body Preview:**\n"
