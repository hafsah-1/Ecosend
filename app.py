import streamlit as st
import datetime
import hmac
import io
from report_1 import generate_faculty_activity_report
from report_2 import generate_membership_breakdown_report
from report_3 import generate_activity_per_hub_report
from report_4 import generate_uos_non_uos_activity_report


def check_password():
    """Returns `True` if the user has entered a correct password."""
    
    def login_form():
        """Display the login form."""
        st.title("🔐 PCE Hubs Reports")
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


def create_download_button(df, filename, label):
    """Create a download button for an Excel file."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    st.download_button(
        label=f"📥 {label}",
        data=output,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


def main_app():
    """Main application after authentication."""
    import pandas as pd
    
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
    
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # Report buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📘 Faculty Activity Report", use_container_width=True):
            with st.spinner("Generating..."):
                result = generate_faculty_activity_report()
            st.success("✅ Report generated!")
            # Read the file and offer download
            try:
                df = pd.read_excel(result)
                create_download_button(df, result, "Download Faculty Report")
            except Exception as e:
                st.error(f"Error: {e}")
        
        if st.button("📊 Membership Breakdown", use_container_width=True):
            with st.spinner("Generating..."):
                result = generate_membership_breakdown_report()
            st.success("✅ Report generated!")
            try:
                filename = f"{today}_pce_hub_report.xlsx"
                df = pd.read_excel(filename)
                create_download_button(df, filename, "Download Membership Report")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🌐 Activity per Hub", use_container_width=True):
            with st.spinner("Generating..."):
                result = generate_activity_per_hub_report()
            st.success("✅ Report generated!")
            try:
                df = pd.read_excel(result)
                create_download_button(df, result, "Download Hub Report")
            except Exception as e:
                st.error(f"Error: {e}")
        
        if st.button("🏫 UoS vs Non-UoS", use_container_width=True):
            with st.spinner("Generating..."):
                result = generate_uos_non_uos_activity_report()
            st.success("✅ Report generated!")
            try:
                df = pd.read_excel(result)
                create_download_button(df, result, "Download UoS Report")
            except Exception as e:
                st.error(f"Error: {e}")


# Need pandas for download functionality
import pandas as pd

# Run the app
if check_password():
    main_app()
