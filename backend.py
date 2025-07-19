import streamlit as st
import sqlite3
import random
import string
import hashlib
from datetime import datetime
import config as cfg


# --- Helper: Hash API Key ---
def hash_api_key(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()


# --- Create Table ---
def create_api_keys_table_if_not_exists():
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            email TEXT,
            api_key_name TEXT UNIQUE,
            hashed_api_key TEXT,
            created_at TIMESTAMP,
            usage_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


# --- Generate Secure API Key ---
def generate_api_key():
    return 'sk-user-' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))


# --- Show API Key Only Once ---
@st.dialog("🚨 Copy your new API key now!")
def show_api_key_first_time(api_key, api_key_name):
    st.markdown(f"**API Key Name:** `{api_key_name}`")
    st.code(api_key, language="plaintext")
    st.warning("This is the only time you'll see this key. Copy it securely.")


# --- Create New API Key ---
def create_api_key():
    st.subheader("🔑 Create API Key")
    api_key_name = st.text_input("Enter a name for your API key:")
    if st.button("Generate API Key"):
        if api_key_name:
            conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
            c = conn.cursor()

            # Check for uniqueness
            c.execute('SELECT 1 FROM api_keys WHERE email = ? AND api_key_name = ?', (st.session_state.email, api_key_name))
            if c.fetchone():
                st.warning("❌ An API key with this name already exists. Choose a unique name.")
                conn.close()
                return

            api_key = generate_api_key()
            hashed_key = hash_api_key(api_key)
            created_at = datetime.now()

            c.execute('INSERT INTO api_keys (email, api_key_name, hashed_api_key, created_at) VALUES (?, ?, ?, ?)', 
                      (st.session_state.email, api_key_name, hashed_key, created_at))
            conn.commit()
            conn.close()
            show_api_key_first_time(api_key, api_key_name)
        else:
            st.warning("Please provide a name for the API key.")


# --- Delete API Key ---
def delete_api_key():
    st.subheader("🗑️ Delete API Key")
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()

    c.execute('SELECT api_key_name, hashed_api_key FROM api_keys WHERE email = ?', (st.session_state.email,))
    keys = c.fetchall()

    if not keys:
        st.info("You have no API keys to delete.")
        return

    display_options = [f"{name}" for name, _ in keys]
    selected = st.selectbox("Choose key to delete:", display_options)

    if st.button("Delete Selected Key"):
        c.execute('DELETE FROM api_keys WHERE email = ? AND api_key_name = ?', (st.session_state.email, selected))
        conn.commit()
        st.success(f"✅ API key '{selected}' deleted successfully.")
    conn.close()


# --- Display Existing API Keys (Masked) ---
@st.fragment(run_every=10)
def display_api_keys():
    st.subheader("🔍 Your API Keys")
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()

    c.execute('''
        SELECT api_key_name, hashed_api_key, created_at, usage_count
        FROM api_keys WHERE email = ?
        ORDER BY created_at DESC
    ''', (st.session_state.email,))
    rows = c.fetchall()
    conn.close()

    if rows:
        table_md = "| Name | Hashed Key  | Created At | Usage Count |\n"
        table_md += "|------|------------------------|-------------|--------------|\n"
        for name, hashed_key, created_at, usage in rows:
            short_hash = hashed_key[:8] + "..." + hashed_key[-4:]
            table_md += f"| {name} | {short_hash} | {created_at} | {usage} |\n"
        st.markdown(table_md)
    else:
        st.info("You haven't generated any API keys yet.")
