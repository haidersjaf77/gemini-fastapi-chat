# --- app.py ---
# Streamlit frontend for OTP login + API key management (calls backend.py)

import streamlit as st
from author import create_users_table_if_not_exists, log_in_mechanism, log_out_mechanism
from backend import create_api_keys_table_if_not_exists, create_api_key, delete_api_key, display_api_keys

st.set_page_config(page_title="ThinkyBot Auth Portal", layout="centered")

toggle = st.sidebar.toggle("🌙 Dark Mode", value=True)
background = "#000814" if toggle else "#f7f9fc"
text_color = "#00bfff" if toggle else "#111"
input_bg = "#001d3d" if toggle else "#fff"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {background};
        color: {text_color};
        font-family: 'Courier New', monospace;
    }}
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stTextInput label, .stButton>button {{
        color: {text_color};
    }}
    .stButton>button {{
        background-color: {input_bg};
        border-radius: 6px;
        border: 1px solid {text_color};
        color: {text_color};
    }}
    .stTextInput>div>div>input {{
        background-color: {input_bg};
        color: {text_color};
    }}
    .stSelectbox>div>div>div>div {{
        background-color: {input_bg};
        color: {text_color};
    }}
    .stSuccess {{
        background-color: #003566;
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

# --- Branded Header ---
st.markdown("""
    <div style="text-align: center;">
        <h1 style="font-size: 3rem;">🤖 ThinkyBot Access Panel</h1>
        <p style="font-size: 1.2rem; color: #6c757d;">
            Secure login, generate API keys, and start chatting smartly!
        </p>
    </div>
""", unsafe_allow_html=True)

# --- Initialize DB Tables ---
create_users_table_if_not_exists()
create_api_keys_table_if_not_exists()

# --- Login Flow ---
if not st.session_state.get("logged_in"):
    log_in_mechanism()
    st.stop()

# --- Logout ---
log_out_mechanism()

st.markdown(f"""
### 👋 Welcome, **{st.session_state.email}**
Here's what you can do next:
- ✅ Generate secure API keys
- ❌ Delete keys you no longer need
- 📊 Track usage in real time
""")

# --- UI Tabs ---
tabs = st.tabs(["🗝️ API Key Manager", "📊 Usage & Stats"])

with tabs[0]:
    col1, col2 = st.columns([1, 1])
    with col1:
        create_api_key()
        delete_api_key()
    with col2:
        st.markdown("""
        #### 🔐 How It Works
        - Your email is your ID
        - Keep your API key private
        - Track and manage your usage easily
        """)

with tabs[1]:
    display_api_keys()
