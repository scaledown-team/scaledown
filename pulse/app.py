"""
Pulse Ecosystem - Web Interface
Built with Streamlit.
"""

import streamlit as st
import time
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from pulse.config import get_default_config
from pulse.core.brain import Brain

# Configure page settings
st.set_page_config(
    page_title="Groot AI",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #E8F5E9; /* Light Green */
    }
    .user-avatar {
        background-color: #8D6E63; /* Brown */
    }
    .assistant-avatar {
        background-color: #2E7D32; /* Dark Green */
    }
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1E1E1E;
    }
    .stButton button {
        border-radius: 20px;
    }
    /* ScaleDown badge */
    .sd-badge {
        background-color: #3E2723; /* Dark Brown */
        color: #A1887F; /* Light Brown */
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_brain():
    """Initialize Brain singleton."""
    config = get_default_config()
    return Brain(config)



# Voice Integration
@st.cache_resource
class VoiceManager:
    def __init__(self):
        self._thread = None
        self._loop = None
        self._stop_event = threading.Event()
        
    def start(self, brain):
        if self._thread and self._thread.is_alive():
            return
            
        from pulse.voice.voice_loop import VoiceLoop
        # We need to ensure we don't block the UI
        # VoiceLoop normally runs in its own thread, but here we manage the high level
        
        self._loop = VoiceLoop(brain, brain.config)
        self._thread = threading.Thread(target=self._loop.start, daemon=True)
        self._thread.start()
        
    def stop(self):
        if self._loop:
            self._loop.stop()
            self._loop = None
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None
            
    def is_running(self):
         return bool(self._loop and self._loop.running)

@st.cache_resource
def get_voice_manager():
    return VoiceManager()

def main():
    brain = get_brain()
    voice_manager = get_voice_manager()

    # Sidebar Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Voice Controls
        st.subheader("🎤 Voice Control")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Voice", type="primary", disabled=voice_manager.is_running()):
                try:
                    voice_manager.start(brain)
                    st.success("Voice activated!")
                    time.sleep(0.5)
                except Exception as e:
                    st.error(f"Failed to start voice: {e}")
                st.rerun()
                
        with col2:
            if st.button("Stop Voice", type="secondary", disabled=not voice_manager.is_running()):
                voice_manager.stop()
                st.rerun()
                
        if voice_manager.is_running():
            st.success("🎙️ Voice Active - Listening...")
            st.caption(f"Wake words: {', '.join(brain.config.wake_words)}")
            db_count = len(brain.memory.get_history(limit=1000))
            st.caption(f"Messages in DB: {db_count}")
        else:
            st.info("🔇 Voice Inactive")

        st.divider()
        
        model_options = [brain.config.default_model]
        if brain.config.openrouter_api_key:
            available = sorted([m for m in brain.llm._get_available_models() if m.endswith(":free")])
            if available:
                model_options = available

        selected_model = st.selectbox(
            "Select Model",
            options=model_options,
            index=model_options.index(brain.config.default_model) if brain.config.default_model in model_options else 0,
            help="Choose the OpenRouter model"
        )
        
        # Update config if model changes
        if selected_model != brain.config.default_model:
            brain.config.default_model = selected_model
            brain.llm.default_model = selected_model
        
        st.divider()
        
        # Context Optimization Settings
        st.subheader("🧠 ScaleDown")
        context_opt = st.toggle("Enable Context Optimization", value=True)
        brain.config.enable_context_optimization = context_opt
        
        if context_opt:
            st.code(f"Strategy: Haste + Compress\nRate: {brain.config.compression_rate}", language="text")
            st.success("Context optimization active")
        else:
            st.warning("Sending raw full history")
            
        st.divider()
        
        # Memory actions
        if st.button("Clear Conversation History", type="primary"):
            brain.clear_memory()
            st.session_state.messages = []
            st.rerun()

    # Main Chat Interface
    st.title("🌳 Groot AI")
    st.caption("I am Groot. (Powered by ScaleDown & OpenRouter)")

    # --- DB-DRIVEN UI SYNC ---
    # Always fetch latest history from Brain Memory to ensure voice chats show up
    # We use a larger limit to show context
    db_history = brain.memory.get_history(limit=50)
    
    # Initialize session state for tracking last message count
    if 'last_message_count' not in st.session_state:
        st.session_state.last_message_count = 0
    
    # st.session_state.messages is now just a cache/buffer for the UI render
    # We rebuild it from DB every time to catch external changes (Voice)
    def _ui_role(role: str) -> str:
        if role == "assistant" or role == "ai":
            return "assistant"
        if role == "user" or role == "human":
            return "user"
        return "assistant"

    st.session_state.messages = [{"role": _ui_role(msg.role), "content": msg.content} for msg in db_history]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message to UI immediately (optimistic update)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Stream response
                # Note: stream_thought handles adding to memory internally
                for chunk in brain.stream_thought(prompt):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                
    # --- AUTO-REFRESH FOR VOICE ---
    # If voice is running, check for new messages and auto-refresh
    if voice_manager.is_running():
        current_message_count = len(st.session_state.messages)
        
        # If message count changed (voice added message), rerun to show it
        if current_message_count != st.session_state.last_message_count:
            st.session_state.last_message_count = current_message_count
            st.rerun()
        
        # Auto-refresh every few seconds to check for new messages
        time.sleep(1.5)
        st.rerun()

if __name__ == "__main__":
    main()
