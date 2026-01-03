import streamlit as st
import datetime
import hmac
import io
import pandas as pd
from report_1 import generate_faculty_activity_report
from report_2 import generate_membership_breakdown_report
from report_3 import generate_activity_per_hub_report
from report_4 import generate_uos_non_uos_activity_report


def check_password():
    """Returns `True` if the user has entered a correct password."""
    
    def login_form():
        """Display the login form."""
        st.title("🔐 EcosendPCE Hubs Reports")
        st.write("Please log in to access the report generator.")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)
            
            if submitted:
                if check_credentials(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("😕 Invalid username or password")
    
    def check_credentials(username, password):
        """Check if username and password are correct."""
        try:
            correct_username = st.secrets["auth"]["username"]
            correct_password = st.secrets["auth"]["password"]
        except (KeyError, FileNotFoundError):
            correct_username = "pce_admin"
            correct_password = "pcehubs2024"
        
        username_match = hmac.compare_digest(username, correct_username)
        password_match = hmac.compare_digest(password, correct_password)
        
        return username_match and password_match
    
    if st.session_state.get("authenticated"):
        return True
    
    login_form()
    return False


def offer_download(filename, label):
    """Read an Excel file and offer it for download."""
    try:
        with open(filename, 'rb') as f:
            file_data = f.read()
        
        st.download_button(
            label=f"📥 {label}",
            data=file_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Download error: {e}")


def main_app():
    """Main application after authentication."""
    
    st.set_page_config(page_title="Ecosend Report Generator", layout="centered")
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.write(f"👤 Logged in as: **{st.session_state.get('username', 'User')}**")
        if st.button("🚪 Log Out"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.rerun()
        
        st.divider()
        st.caption("PCE Hubs Southampton")
        st.caption("Powered by Ecosend")
    
    # Page title
    st.title("📬 Ecosend Reports")
    st.write("Generate engagement and membership reports.")
    
    # Report buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📘 Faculty Activity Report", use_container_width=True):
            with st.spinner("Generating..."):
                filename = generate_faculty_activity_report()
            st.success(f"✅ Generated: `{filename}`")
            offer_download(filename, "Download Faculty Report")
        
        if st.button("📊 Membership Breakdown", use_container_width=True):
            with st.spinner("Generating..."):
                filename = generate_membership_breakdown_report()
            st.success(f"✅ Generated: `{filename}`")
            offer_download(filename, "Download Membership Report")
    
    with col2:
        if st.button("🌐 Activity per Hub", use_container_width=True):
            with st.spinner("Generating..."):
                filename = generate_activity_per_hub_report()
            st.success(f"✅ Generated: `{filename}`")
            offer_download(filename, "Download Hub Report")
        
        if st.button("🏫 UoS vs Non-UoS", use_container_width=True):
            with st.spinner("Generating..."):
                filename = generate_uos_non_uos_activity_report()
            st.success(f"✅ Generated: `{filename}`")
            offer_download(filename, "Download UoS Report")


# Run the app
if check_password():
    main_app()
