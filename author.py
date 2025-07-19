import os
import sys
import time
import random
import sqlite3
from datetime import datetime, timedelta
import streamlit as st
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import config as cfg

if not load_dotenv():
    print("Credentials env file not found!")
    sys.exit(1)

def create_users_table_if_not_exists():
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    otp TEXT,
                    otp_expiry TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(recipient_email, recipient_otp):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        sender_email = os.getenv("GMAIL_EMAIL")
        app_password = os.getenv("GMAIL_APP_PASSWORD")

        html_content = cfg.OTP_EMAIL_HTML.format(generated_otp=recipient_otp)
        msg = MIMEText(html_content, 'html')
        msg['Subject'] = 'Your OTP Code'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False

def validate_otp(email, otp_input):
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT otp, otp_expiry FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    if result:
        stored_otp, otp_expiry = result
        if stored_otp == otp_input and datetime.now() <= datetime.strptime(otp_expiry, '%Y-%m-%d %H:%M:%S.%f'):
            return True
    return False

def get_otp_and_exipry(email):
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT otp, otp_expiry FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    return result

def update_otp(email, otp, otp_expiry):
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('REPLACE INTO users (email, otp, otp_expiry) VALUES (?, ?, ?)', (email, otp, otp_expiry))
    conn.commit()
    conn.close()

def is_supported_domain(email):
    domain = email.split('@')[-1]
    return domain in cfg.SUPPORTED_DOMAINS

def log_in_mechanism():
    email = st.text_input("Enter your email:")
    if st.button("Submit Email"):
        with st.spinner('Verifying and sending you email'):
            if email:
                email_strip = email.strip()
                if is_supported_domain(email_strip):
                    otp_result = get_otp_and_exipry(email_strip)
                    current_time = datetime.now()
                    if otp_result and datetime.strptime(otp_result[1], '%Y-%m-%d %H:%M:%S.%f') > current_time:
                        generated_otp = otp_result[0]
                    else:
                        generated_otp = generate_otp()
                        otp_expiry = current_time + timedelta(minutes=10)
                        update_otp(email_strip, generated_otp, otp_expiry)

                    if send_otp(email_strip, generated_otp):
                        st.session_state.email = email_strip
                        st.session_state.show_otp_input = True
                        st.success("OTP has been sent to your email.")
                    else:
                        st.error("Failed to send OTP. Please try again later.")
                else:
                    st.warning(f"Unsupported domain. Use one of: {', '.join(cfg.SUPPORTED_DOMAINS)}")
            else:
                st.warning("Enter a valid email address.")

    if st.session_state.get('show_otp_input'):
        otp_input = st.text_input("Enter OTP:", type="password")
        if st.button("Verify OTP"):
            if otp_input:
                if validate_otp(st.session_state.email, otp_input):
                    st.success(f"Login successful! Welcome, {st.session_state.email}.")
                    st.session_state.logged_in = True
                    st.session_state.show_otp_input = False
                    st.rerun()
                else:
                    st.error("Invalid or expired OTP.")
            else:
                st.warning("Please enter the OTP sent to your email.")

def log_out_mechanism():
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.email = ''
        st.session_state.key_verified = False
        st.session_state.current_user_key = ''
        st.rerun()