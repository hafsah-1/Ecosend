import streamlit as st
import datetime
import hmac
from report_1 import generate_faculty_activity_report
from report_2 import generate_membership_breakdown_report
from report_3 import generate_activity_per_hub_report
from report_4 import generate_uos_non_uos_activity_report


def check_password():
    """Returns `True` if the user has entered a correct password."""
    
    def login_form():
        """Display the login form."""
        st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
        
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
        # Get credentials from Streamlit secrets (for cloud) or environment
        try:
            correct_username = st.secrets["auth"]["username"]
            correct_password = st.secrets["auth"]["password"]
        except (KeyError, FileNotFoundError):
            # Fallback to default for local development
            # CHANGE THESE for production!
            correct_username = "pce_admin"
            correct_password = "pcehubs2024"
        
        # Use constant-time comparison to prevent timing attacks
        username_match = hmac.compare_digest(username, correct_username)
        password_match = hmac.compare_digest(password, correct_password)
        
        return username_match and password_match
    
    # Check if already authenticated
    if st.session_state.get("authenticated"):
        return True
    
    # Show login form
    login_form()
    return False


def main_app():
    """Main application after authentication."""
    
    # Set up the Streamlit page title
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
    
    # Page title and description
    st.title("📬 Ecosend Reports")
    st.write("Generate engagement and membership reports based on Ecosend contact data.")
    
    # Get today's date for report success message
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    
    # Create the form layout with two columns
    with st.form(key="report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            faculty_btn = st.form_submit_button("📘 Generate Faculty Activity Report", use_container_width=True)
            breakdown_btn = st.form_submit_button("📊 Generate Membership Breakdown Report", use_container_width=True)
        
        with col2:
            hub_btn = st.form_submit_button("🌐 Generate Activity per Hub Report", use_container_width=True)
            uos_btn = st.form_submit_button("🏫 Generate UoS vs Non-UoS Activity Report", use_container_width=True)
    
    # Handle the button presses and call respective report functions
    if faculty_btn:
        with st.spinner("Generating Faculty Activity Report..."):
            result = generate_faculty_activity_report()
        st.success(f"✅ Faculty Activity Report generated: `{result}`")
        st.balloons()
    
    if breakdown_btn:
        with st.spinner("Generating Membership Breakdown Report..."):
            result = generate_membership_breakdown_report()
        st.success(f"✅ Membership Breakdown Report generated! ({today})")
        st.balloons()
    
    if hub_btn:
        with st.spinner("Generating Activity per Hub Report..."):
            result = generate_activity_per_hub_report()
        st.success(f"✅ Activity per Hub Report generated: `{result}`")
        st.balloons()
    
    if uos_btn:
        with st.spinner("Generating UoS vs Non-UoS Activity Report..."):
            result = generate_uos_non_uos_activity_report()
        st.success(f"✅ UoS vs Non-UoS Activity Report generated: `{result}`")
        st.balloons()


# Run the app
if check_password():
    main_app()
