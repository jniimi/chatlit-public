from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic
import streamlit as st
from llm_clients import get_response_chatgpt, get_response_claude, get_response_gemini

if "initialized" not in st.session_state:
    st.session_state['api'] = {'openai': '', 'google': '', 'anthropic': ''}
    st.session_state['client'] = {}
    st.session_state['selected_model'] = None
    st.session_state['initialized'] = True

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="key1", type="password")
    google_api_key = st.text_input("Google API Key", key="key2", type="password")
    anthropic_api_key = st.text_input("Anthropic API Key", key="key3", type="password")

    st.divider()
    st.header("⚙️ Settings")
    
    model_id_gpt = st.selectbox(
        "ChatGPT",
        options=[
            "gpt-5-mini-2025-08-07",
            "gpt-5-2025-08-07",
            "gpt-4o",
            "gpt-4o-mini",
        ], index=0, help="Choose the OpenAI ChatGPT model_id.")
    model_id_gemini = st.selectbox(
        "Gemini",
        options=[
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ], index=0, help="Choose the Google Gemini model_id.")
    model_id_claude = st.selectbox(
        "Claude",
        options=[
            "claude-sonnet-4-20250514",
            "claude-opus-4-1-20250805",
            "claude-opus-4-20250514"
        ], index=0, help="Choose the Anthropic Claude model_id.")


if st.session_state['api']['openai'] != openai_api_key:
    st.session_state['api']['openai'] = openai_api_key
    st.session_state['client']['openai'] = OpenAI(api_key=openai_api_key)

if st.session_state['api']['google'] != google_api_key:
    st.session_state['api']['google'] = google_api_key
    st.session_state['client']['google'] = genai.configure(api_key=google_api_key)

if st.session_state['api']['anthropic'] != anthropic_api_key:
    st.session_state['api']['anthropic'] = anthropic_api_key
    st.session_state['client']['anthropic'] = Anthropic(api_key=anthropic_api_key)



# Header (Title and Descriptions)
header_container = st.container()
with header_container:
    st.title("💬 ChatreamLit")
    st.caption("🚀 Multi-LLM chatting service by jniimilab.")

# Display chat messages (placeholder for dynamic content)
messages_placeholder = st.empty()

# User Input (chat_input placed here)
submission_container = st.container()
with submission_container:
    prompt = st.chat_input()

# Model Select
button_container = st.container()
with button_container:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 ChatGPT", use_container_width=True, 
                    type="primary" if st.session_state.get('selected_model') == "chatgpt" else "secondary"):
            st.session_state['selected_model'] = "chatgpt"
            st.html("<script>window.scrollTo(0, document.body.scrollHeight);</script>")
            st.rerun()
    
    with col2:
        if st.button("🤖 Claude", use_container_width=True,
                    type="primary" if st.session_state.get('selected_model') == "claude" else "secondary"):
            st.session_state['selected_model'] = "claude"
            st.html("<script>window.scrollTo(0, document.body.scrollHeight);</script>")
            st.rerun()
    
    with col3:
        if st.button("✨ Gemini", use_container_width=True,
                    type="primary" if st.session_state.get('selected_model') == "gemini" else "secondary"):
            st.session_state['selected_model'] = "gemini"
            st.html("<script>window.scrollTo(0, document.body.scrollHeight);</script>")
            st.rerun()

# Fill messages placeholder with chat history and handle new messages
with messages_placeholder.container():
    # Display existing messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    
    # Process new input if there is any
    if prompt:
        if st.session_state['selected_model'] is None:
            st.warning("Please select a model (ChatGPT, Claude, or Gemini) before sending a message.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            with st.spinner(f"Getting response from {st.session_state['selected_model'].title()}..."):
                try:
                    if st.session_state['selected_model'] == "chatgpt":
                        msg = get_response_chatgpt(prompt, st.session_state.messages, 
                                                st.session_state['client']['openai'], model_id_gpt)
                    elif st.session_state['selected_model'] == "claude":
                        msg = get_response_claude(prompt, st.session_state.messages, 
                                                st.session_state['client']['anthropic'], model_id_claude)
                    elif st.session_state['selected_model'] == "gemini":
                        msg = get_response_gemini(prompt, st.session_state.messages, model_id_gemini)
                        if 'assistant:' in msg:
                            msg = msg.split('assistant:')[1]
                        if 'Assistant:' in msg:
                            msg = msg.split('Assistant:')[1]
                        if 'ASSISTANT:' in msg:
                            msg = msg.split('ASSISTANT:')[1]
                    
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.chat_message("assistant").write(msg)
                    
                    # Save conversation to history
                    st.session_state['history_manager'].save_conversation(
                        st.session_state['current_session_id'],
                        st.session_state.messages,
                        st.session_state['selected_model']
                    )
                except Exception as e:
                    st.error(f"Error getting response from {st.session_state['selected_model']}: {str(e)}")

