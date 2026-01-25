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
        st.markdown("""
            <style>
            .login-header {
                text-align: center;
                padding: 2rem 0;
            }
            </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔐 PCE Hubs Reports")
            st.caption("Powered by Ecosend")
            st.write("")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                st.write("")
                submitted = st.form_submit_button("Log In", use_container_width=True, type="primary")
                
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


def report_card(title, icon, description, button_label, generate_func, download_label):
    """Create a styled report card with description."""
    with st.container(border=True):
        st.subheader(f"{icon} {title}")
        st.caption(description)
        st.write("")
        
        if st.button(button_label, key=title, use_container_width=True, type="primary"):
            with st.spinner("Generating report..."):
                filename = generate_func()
            st.success(f"✅ Report generated!")
            offer_download(filename, download_label)


def main_app():
    """Main application after authentication."""
    
    st.set_page_config(
        page_title="PCE Hubs Report Generator",
        page_icon="📊",
        layout="centered"
    )
    
    # Custom CSS for nicer styling
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
            margin-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar with user info and logout
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/email-open.png", width=60)
        st.title("PCE Hubs")
        st.caption("Report Generator")
        
        st.divider()
        
        st.write(f"👤 **{st.session_state.get('username', 'User')}**")
        
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.rerun()
        
        st.divider()
        
        st.caption("University of Southampton")
        st.caption("Public & Community Engagement Hubs")
    
    # Page header
    st.title("📊 Report Generator")
    st.markdown("Generate engagement and membership reports from your Ecosend data.")
    st.write("")
    
    # Membership Reports Section (most used - first)
    st.subheader("👥 Membership Reports")
    st.caption("Breakdown of contacts by hub, faculty, and status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("##### 📊 Membership Breakdown")
            st.caption("Full breakdown of contacts per Hub, showing UoS status, alumni status, and faculty distribution.")
            st.write("")
            if st.button("Generate Membership Report", key="membership", use_container_width=True, type="primary"):
                with st.spinner("Generating..."):
                    filename = generate_membership_breakdown_report()
                st.success("✅ Done!")
                offer_download(filename, "Download Report")
    
    with col2:
        pass  # Empty for now
    
    st.write("")
    st.divider()
    
    # Activity Reports Section  
    st.subheader("📈 Activity Reports")
    st.caption("Track engagement based on the 'Active (Last 90 Days)' smart group")
    
    # Help expander with instructions
    with st.expander("ℹ️ **Before generating**: Update the Active smart group in Ecosend"):
        st.markdown("""
        ⚠️ **Important**: Ecosend doesn't provide broadcast activity data through its API, so we track activity using a manually-maintained Smart Group.
        
        **Before generating activity reports, update the 'Active (Last 90 Days)' smart group:**
        
        ---
        
        **Step 1:** Go to [Ecosend](https://app.ecosend.io), click on **Contacts**, then scroll down on the left sidebar to find **Smart Groups**
        
        **Step 2:** Find and open the **"Active (Last 90 Days)"** smart group
        
        **Step 3:** Update the filter rules:
        - Click the **Messages** tab in the filter menu
        - Select **"Opened message"** 
        - Add each broadcast from the **last 90 days** using **+ OR** between them
        - Remove any broadcasts older than 90 days
        """)
        
        st.image("images/ecosend_messages_menu.png", caption="Select 'Opened message' from the Messages tab", width=400)
        st.image("images/ecosend_filter_bar.png", caption="Add broadcasts with '+ OR' between them")
        
        st.markdown("""
        **Step 4:** Click **★ Save Smart Group** to save your changes
        
        **Step 5:** Come back here and generate your reports!
        """)
    
    st.write("")
    
    col3, col4 = st.columns(2)
    
    with col3:
        with st.container(border=True):
            st.markdown("##### 📘 Faculty Activity")
            st.caption("Shows member counts and activity rates broken down by faculty (FAH, FELS, FEPS, FM, FSS, Professional Services).")
            st.write("")
            if st.button("Generate Faculty Report", key="faculty", use_container_width=True, type="primary"):
                with st.spinner("Generating..."):
                    filename = generate_faculty_activity_report()
                st.success("✅ Done!")
                offer_download(filename, "Download Report")
    
    with col4:
        with st.container(border=True):
            st.markdown("##### 🌐 Activity per Hub")
            st.caption("Shows member counts and activity rates for each PCE Hub (AI & Society, Health, Nature, Future Cities).")
            st.write("")
            if st.button("Generate Hub Report", key="hub", use_container_width=True, type="primary"):
                with st.spinner("Generating..."):
                    filename = generate_activity_per_hub_report()
                st.success("✅ Done!")
                offer_download(filename, "Download Report")
    
    col5, col6 = st.columns(2)
    
    with col5:
        with st.container(border=True):
            st.markdown("##### 🏫 UoS vs Non-UoS")
            st.caption("Compares activity rates between current University of Southampton members and external contacts.")
            st.write("")
            if st.button("Generate UoS Report", key="uos", use_container_width=True, type="primary"):
                with st.spinner("Generating..."):
                    filename = generate_uos_non_uos_activity_report()
                st.success("✅ Done!")
                offer_download(filename, "Download Report")
    
    with col6:
        pass  # Empty for now


# Run the app
if check_password():
    main_app()
