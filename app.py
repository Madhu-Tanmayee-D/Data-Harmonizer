"""
Streamlit application for Dataset Harmonization Pipeline
Frontend for uploading, processing, and downloading harmonized datasets
"""
import streamlit as st
import pandas as pd
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import json

# Local asset paths
ROOT_DIR = Path(__file__).resolve().parent
LOGO_PATH = ROOT_DIR / "Logo.png"

# Import custom modules
from config import UPLOADS_DIR, OUTPUTS_DIR
from database import init_database, DB_PATH
from auth import register_user, login_user, get_user_info, user_exists
from db_utils import (
    save_upload_record, get_user_uploads, save_processing_record,
    update_processing_status, save_download_record, get_user_processing_history,
    get_user_download_history, get_processing_details, get_download_file_path
)
from pipeline import run_pipeline

# Page configuration
st.set_page_config(
    page_title="Dataset Harmonization Platform",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_logo(size=120):
    # Increasing the side column weights (e.g., 4, 2, 4)
    # creates more padding on the sides to force the middle to be centered.
    c1, c2, c3 = st.columns([4, 2, 3])
    with c2:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=size)

import streamlit.components.v1 as components

def auto_focus(key):
    """
    Inject JavaScript to focus on a text_input component by its specific key.
    """
    # We look for the container that holds the key in its data-testid
    js = f"""
    <script>
        setTimeout(() => {{
            var container = window.parent.document.querySelector('div[data-testid="stTextInput"][data-baseweb="input"]');
            // This is a more direct way to find the input within your specific key
            var input = window.parent.document.querySelector('input[aria-label="Filename for your harmonized dataset:"]');
            if (input) {{
                input.focus();
            }}
        }}, 500); 
    </script>
    """
    components.html(js, height=0, width=0)

# Custom CSS - Cyber Emerald & Charcoal Theme with precise structural overrides
st.markdown("""
<style>
    /* Import Space Grotesk from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght=300;400;500;600&display=swap');

    @import url('https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css');

    /* Force browser to use the Remix Icon font family */
    i {
        font-family: 'remixicon' !important;
        speak: none;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
    }
                
    /* Font Family Assignment */
    html, body, [data-testid="stAppViewContainer"] * {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    /* Transparent native top header bar */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        background: transparent !important;
    }
    
    /* Color target the main three dots option context button in the top right */
    button[data-testid="stActionButtonIcon"] svg, 
    div[data-testid="stToolbarOptionsButton"] button svg,
    .stAppHeader [data-testid="stToolbar"] svg {
        fill: #a7f3d0 !important;
        color: #a7f3d0 !important;
    }
    
    /* Pure Dark Charcoal Gradient Canvas */
    div[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0f11 0%, #16161a 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* --- Sleek Sidebar Surface --- */
    
    /* 1. Force background to match your dark theme */
    div[data-testid="stSidebar"],
    div[data-testid="stSidebarContent"],
    div[data-testid="stSidebar"] > div:first-child {
        background-color: #0f0f11 !important;
    }

    div[data-testid="stSidebar"] {
        border-right: 1px solid #222226;
    }

    /* --- Sidebar Text Styling --- */

    /* 1. Login Name (Username Heading): Keep as is */
    div[data-testid="stSidebar"] h3 {
        color: #C48A6A !important; 
    }

    /* 2. Target EVERYTHING inside the sidebar for the new lighter grey */
    /* This overrides button text, captions, and markdown text simultaneously */
    div[data-testid="stSidebar"], 
    div[data-testid="stSidebar"] *, 
    div[data-testid="stSidebar"] button, 
    div[data-testid="stSidebar"] p, 
    div[data-testid="stSidebar"] span,
    div[data-testid="stSidebar"] .stButton > button > div {
        color: #e1b995 !important;
    }

    /* 3. Subtle Dividers */
    div[data-testid="stSidebar"] hr {
        border-color: #2d2d30 !important;
    }
    
    /* Elegant Main Headers */
    .main-header {
        text-align: center;
        color: #C48A6A !important;
        margin-bottom: 1.5rem;
        font-size: 2.8rem !important;
        font-weight: 500;
        letter-spacing: -0.02em;
    }
    
    /* Standard Text Segments - Light Slate */
    div[data-testid="stMarkdownContainer"] p, p {
        color: #94a3b8 !important;
        font-size: 1rem !important;
        font-weight: 300;
    }
    
    /* Section Subheaders & Form Input Titles - Mint/Soft Sage & White */
    h1, h2, h3, h4, h5, h6, [data-testid="stWidgetLabel"] p {
        color: #e1b995 !important;
        font-weight: 400 !important;
    }
    
    h2, [data-testid="stSubheader"] {
        font-size: 1.6rem !important;
        color: #e1b995 !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
        color: #e1b995 !important;
    }

    /* Absolute Left-Aligned Custom Subheader Class for Auth Views */
    .auth-subheader {
        color: #C48A6A !important;
        font-size: 1.6rem !important;
        font-weight: 400 !important;
        max-width: 430px !important;
        margin: 0 auto 1.2rem auto !important;
        text-align: left !important;
    }

    /* Metric Layout Elements Styling */
    span[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }
    
    div[data-testid="stMetricValue"] > div {
        color: #e8f5e9 !important;
        font-size: 1.8rem !important;
        font-weight: 400 !important;
    }

    /* Force-kill any empty native layout container border outlines */
    div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stVerticalBlock"] {
        border: none !important;
        box-shadow: none !important;
    }

    /* Card layout element container tracking box scaled to 460px - Obsidian Tone */
    div.element-container:has(div.auth-card-anchor) + div[data-testid="stVerticalBlock"] {
        max-width: 460px !important;
        margin: 0 auto !important;
        padding: 2.5rem !important;
        border-radius: 12px !important;
        background-color: #16161a !important;
        border: 1px solid #27272a !important;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Spacious & Proportional 430px Wide Custom Input Boxes */
    .stTextInput {
        max-width: 430px !important;
        margin: 0 auto 1rem auto !important;
        text-align: left !important;
    }
    
    .stTextInput > div > div > input {
        background-color: #1f1f23 !important;
        color: #e8f5e9 !important;
        border: 1px solid #27272a !important;
        border-radius: 8px;
        font-size: 0.95rem;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #a7f3d0 !important;
        box-shadow: 0 0 0 1px #a7f3d0 !important;
    }
    
    /* Main Submission Control Buttons mapped perfectly to matching form block bounds (Obsidian Slate) */
    .stButton {
        max-width: 430px !important;
        margin: 0 auto !important;
    }

    .stButton > button {
        background-color: #27272a !important;
        color: #e8f5e9 !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        padding: 0.65rem 2.2rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .stButton > button * {
        color: #e8f5e9 !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #2d2d30 !important;
        border-color: #a7f3d0 !important;
        box-shadow: 0 4px 15px rgba(167, 243, 208, 0.2) !important;
        transform: translateY(-1px);
    }

    /* Redirect Box alignment matching input structural boundaries */
    .redirect-box {
        max-width: 430px !important;
        margin: 1.5rem auto 0 auto !important;
        padding: 0.8rem !important;
        background-color: #1f1f23 !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        text-align: center !important;
    }

    .redirect-link {
        color: #C48A6A !important;
        text-decoration: none !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        background: transparent !important;
        display: block;
        width: 100%;
        cursor: pointer;
    }
    
    .redirect-link:hover {
        color: #e8f5e9 !important;
        text-decoration: underline !important;
    }

    /* Dusk Lavender Captions */
    .stCaption, .stCaption div, .stCaption p {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
    }
    
    .info-box {
        padding: 1rem;
        background-color: #1f1f23;
        border-left: 4px solid #a7f3d0;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Embedded Dataframes matching rules */
    div[data-testid="stDataFrame"] {
        background-color: #16161a !important;
        border: 1px solid #27272a;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Interactive Upload Boxes */
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #131316 !important;
        border: 1px dashed #3f3f46 !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #a7f3d0 !important;
    }
    
    /* Horizontal Dividers */
    hr {
        border-color: #27272a !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
if not os.path.exists(DB_PATH):
    init_database()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'auth_view' not in st.session_state:
    st.session_state.auth_view = 'login'  # 'login' or 'signup'


def get_safe_filename(name: str) -> str:
    safe = "".join([c for c in name if c.isalnum() or c in ('-', '_', '.')]).strip()
    return safe or "dataset"


def save_uploaded_file(uploaded_file, target_dir: Path, user_id: int) -> str:
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_name = get_safe_filename(uploaded_file.name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    storage_name = f"{user_id}_{timestamp}_{safe_name}"
    storage_path = target_dir / storage_name
    uploaded_file.seek(0)
    with open(storage_path, 'wb') as out_file:
        shutil.copyfileobj(uploaded_file, out_file)
    return str(storage_path)


def render_auth_page():
    """Render unified seamless login and signup views cleanly styled."""
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)
    # MOVE LOGO CALLS HERE: This ensures it renders before the title
    render_logo(size=120)
    
    st.markdown("<h1 class='main-header'>Dataset Harmonization</h1>", unsafe_allow_html=True)
    
    # Inject a clean anchor element
    st.markdown("<div class='auth-card-anchor'></div>", unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.auth_view == 'login':
        
            st.markdown("<div class='auth-subheader'>Login</div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                if username and password:
                    success, user_id, message = login_user(username, password)
                    if success:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success(f"✅ Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("Please fill in all fields")
            
            # Use query parameters to trigger state rerouting perfectly without generating standard Streamlit button divs
            st.markdown("""
                <div class='redirect-box'>
                    <a href='?action=signup' target='_self' class='redirect-link'>
                        If you don't have an account, you can sign up here!
                    </a>
                </div>
            """, unsafe_allow_html=True)
        
        elif st.session_state.auth_view == 'signup':
            st.markdown("<div class='auth-subheader'>Create Account</div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="signup_username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Sign Up", use_container_width=True):
                if not (username and email and password and confirm_password):
                    st.warning("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords don't match")
                else:
                    success, message = register_user(username, email, password)
                    if success:
                        st.success(f"✅ {message}\nYou can now login!")
                        st.session_state.auth_view = 'login'
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                        
            st.markdown("""
                <div class='redirect-box'>
                    <a href='?action=login' target='_self' class='redirect-link'>
                        Already have an account? Log in here!
                    </a>
                </div>
            """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with navigation."""
    
    # 1. Logo section at the top of the sidebar
    c1, c2, c3 = st.sidebar.columns([1, 2, 1])
    with c2:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=100)
    
    # Minimal space between logo and user info
    st.sidebar.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    
    # 2. User info section
    st.sidebar.markdown(f"### <span style='color: #e1b995;'>✦ <span style='color: #e1b995;'>{st.session_state.username}</span>", unsafe_allow_html=True)
    user_info = get_user_info(st.session_state.user_id)
    if user_info:
        st.sidebar.markdown(f'<span style="font-size: 0.8rem;">✉ {user_info["email"]}</span>', unsafe_allow_html=True)
    st.sidebar.divider()
    
    # Helper to maintain uniform button sizes
    def centered_button(label, key):
        c1, c2, c3 = st.sidebar.columns([1, 3, 1])
        with c2:
            return st.button(label, key=key, use_container_width=True)

    # 3. Navigation
    # Very tight spacing (10px) instead of <br>
    st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if centered_button("❖ Dashboard", "btn_dash"):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    # Tight spacing between Dashboard and History
    st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    if centered_button("▤ History", "btn_hist"):
        st.session_state.current_page = 'history'
        st.rerun()

    # Tight spacing before divider
    st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # 4. Logout
    st.sidebar.divider()
    if centered_button("⎋ Logout", "btn_logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.auth_view = 'login'
        st.query_params.clear()
        st.rerun()

def render_dashboard():
    """Render main dashboard page."""
    
    # 1. Consolidated CSS Injection
    st.markdown("""
        <style>
            /* File Uploader Styles */
            div[data-testid="stFileUploader"] span { color: #FFFFFF !important; }
            div[data-testid="stFileUploader"] section {
                background-color: #27272a !important;
                border: 2px dashed #52525b !important;
                border-radius: 10px !important;
            }
            div[data-testid="stFileUploader"] button {
                background-color: #3f3f46 !important;
                color: #FFFFFF !important;
            }
            /* Dataframe Styles */
            [data-testid="stDataFrame"] { background-color: #27272a !important; }
            [data-testid="stDataFrame"] div[role="gridcell"], 
            [data-testid="stDataFrame"] div[role="columnheader"] { font-size: 0.75rem !important; }
            [data-testid="stDataFrame"] div { color: #e4e4e7 !important; }
                
            /* Targeting by button tag and within common Streamlit container classes */
            div.stButton > button, 
            div.stDownloadButton > button {
                background-color: #000000 !important;
                color: #FFFFFF !important;
                border: 1px solid #52525b !important;
                font-weight: bold !important;
                border-radius: 5px !important;
            }

            div.stButton > button:hover, 
            div.stDownloadButton > button:hover {
                background-color: #27272a !important;
                color: #FFFFFF !important;
                border: 1px solid #a1a1aa !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='main-header'>Harmonization</h1>", unsafe_allow_html=True)
    
    # 2. File Upload Section
    st.markdown("""
    <h3 style="display: flex; align-items: center; gap: 10px; color: #e1b995 !important;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e1b995" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 13V3l4 4M12 3L8 7M6 13v6a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-6"/>
        </svg>
        Upload Datasets
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Dataset 1**")
        # The CSS we added earlier will automatically style this uploader
        file1 = st.file_uploader("Choose first dataset", key="file1", type=['csv', 'xlsx', 'xls'])
    with col2:
        st.markdown("**Dataset 2**")
        file2 = st.file_uploader("Choose second dataset", key="file2", type=['csv', 'xlsx', 'xls'])
    
    # Preview section
    # Preview section
    if file1 or file2:
        st.markdown("""
        <h3 style="display: flex; align-items: center; gap: 10px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
            Dataset Preview
        </h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        if file1:
            with col1:
                st.markdown("**Dataset 1 Preview**")
                try:
                    # Perform read
                    if file1.name.lower().endswith(('.xlsx', '.xls')):
                        df1 = pd.read_excel(file1)
                    else:
                        df1 = pd.read_csv(file1)
                    
                    # Render dataframe with limited height
                    st.dataframe(df1.head(5), use_container_width=True, height=125)
                    st.markdown(f'<span style="color: #4b5563; font-weight: bold;">File: {file1.name}</span>', unsafe_allow_html=True)
                    st.caption(f"Rows: {len(df1)} | Columns: {len(df1.columns)}")
                except Exception as e:
                    st.error(f"Could not load Dataset 1: {e}")
        
        if file2:
            with col2:
                st.markdown("**Dataset 2 Preview**")
                try:
                    # Perform read
                    if file2.name.lower().endswith(('.xlsx', '.xls')):
                        df2 = pd.read_excel(file2)
                    else:
                        df2 = pd.read_csv(file2)
                    
                    # Render dataframe with limited height
                    st.dataframe(df2.head(5), use_container_width=True, height=125)
                    st.markdown(f'<span style="color: #4b5563; font-weight: bold;">File: {file2.name}</span>', unsafe_allow_html=True)
                    st.caption(f"Rows: {len(df2)} | Columns: {len(df2.columns)}")
                except Exception as e:
                    st.error(f"Could not load Dataset 2: {e}")
    

    # 4. Processing Section
    if file1 and file2:
        st.markdown("""
        <h3 style="display: flex; align-items: center; gap: 10px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M23 4v6h-6"/>
                <path d="M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            Process Datasets
        </h3>
        """, unsafe_allow_html=True)
        
        
        # 1. Generate a smart default name based on uploaded files
        default_name = f"{os.path.splitext(file1.name)[0]}_{os.path.splitext(file2.name)[0]}_harmonized"
        
       # 2. UI inputs for naming and format
        user_filename = st.text_input(
            "Filename for your harmonized dataset:", 
            value=default_name,
            key="harmonized_name_input"  # This key is required for the auto-focus script
        )
        
        # Call the auto-focus function using the key provided above
        auto_focus("harmonized_name_input")

        output_format = st.radio("Select output format:", ["CSV", "Excel"], horizontal=True)

        if st.button("Start Harmonization", use_container_width=True):
            with st.spinner("Processing your datasets..."):
                try:
                    # Save uploaded files permanently so history download links work
                    file1_path = save_uploaded_file(file1, UPLOADS_DIR, st.session_state.user_id)
                    file2_path = save_uploaded_file(file2, UPLOADS_DIR, st.session_state.user_id)
                    
                    # Save upload records
                    ext1 = os.path.splitext(file1.name)[1].lstrip('.').lower()
                    ext2 = os.path.splitext(file2.name)[1].lstrip('.').lower()
                    ext1 = 'xlsx' if ext1 in ['xls', 'xlsx'] else ext1
                    ext2 = 'xlsx' if ext2 in ['xls', 'xlsx'] else ext2

                    upload_id_1 = save_upload_record(st.session_state.user_id, file1.name, file1_path, file1.size, ext1 or 'csv')
                    upload_id_2 = save_upload_record(st.session_state.user_id, file2.name, file2_path, file2.size, ext2 or 'csv')
                    
                    # Save processing record
                    process_id = save_processing_record(st.session_state.user_id, upload_id_1, upload_id_2)
                    
                    # Run pipeline
                    harmonized_outputs = run_pipeline([file1_path, file2_path])
                    
                    # Combine DataFrames
                    combined_df = pd.concat(harmonized_outputs.values(), ignore_index=True)
                    
                    # 3. Handle Naming and Extension
                    safe_filename = get_safe_filename(user_filename)
                    if not safe_filename:
                        safe_filename = "harmonized_output"
                    
                    # 3. Handle Naming and Extension
                    extension = ".csv" if output_format == "CSV" else ".xlsx"
                    
                    # This is the name the user will see when downloading
                    download_filename = f"{safe_filename}{extension}"
                    
                    # This is the name used for internal server storage (keeps files unique)
                    storage_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{download_filename}"
                    output_path = OUTPUTS_DIR / storage_filename
                    
                    # 4. Conditional Save and Download prep
                    # Persist harmonized output to disk and prepare a file handle for download
                    if output_format == "CSV":
                        combined_df.to_csv(output_path, index=False)
                        mime_type = "text/csv"
                    else:
                        combined_df.to_excel(output_path, index=False, engine='xlsxwriter')
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    # 5. Finalize Records and Cleanup
                    file_size_bytes = os.path.getsize(output_path)
                    save_download_record(st.session_state.user_id, process_id, download_filename, str(output_path), file_size_bytes)
                    update_processing_status(process_id, 'Completed', None, {'name': download_filename, 'path': str(output_path), 'size': file_size_bytes})
                    
                    st.success("✅ Harmonization completed successfully!")
                    
                    # Display Preview & Download
                    st.subheader("Harmonized Dataset Preview")
                    st.dataframe(combined_df.head(10), use_container_width=True, height=125)
                    st.caption(f"Total Rows: {len(combined_df)} | Total Columns: {len(combined_df.columns)}")
                    
                    # Provide download button for the saved harmonized output
                    file_data = output_path.read_bytes()
                    st.download_button(
                        label=f"📥 Download {output_format} Dataset",
                        data=file_data,
                        file_name=download_filename,
                        mime=mime_type,
                        use_container_width=True
                    )
                    
                except Exception as e:
                    if 'process_id' in locals():
                        update_processing_status(process_id, 'failed', str(e))
                    st.error(f"❌ Error during processing: {str(e)}")


def render_history():
    """Render history page with consistent coloring across all columns."""
    st.markdown("<h1 class='main-header'>History</h1>", unsafe_allow_html=True)
    
    processing_history = get_user_processing_history(st.session_state.user_id)

    if processing_history:
        status_colors = {'Completed': '#22c55e', 'Processing': '#3b82f6', 'Failed': '#ef4444', 'Pending': '#a1a1aa'}
        
        for job in processing_history:
            # Determine the color based on job status
            status_color = status_colors.get(job.get('status'), '#a1a1aa')
            col1, col2, col3, col4 = st.columns([1, 1.2, 1.2, 1.5])
            
            # Headings remain gray and underlined
            heading_style = 'font-size: 0.9rem; color: #a1a1aa; text-transform: uppercase; text-decoration: underline; text-underline-offset: 4px;'
            
            # Content: Applies the status_color to all data fields
            content_style = f'font-size: 0.85rem; margin-top: 5px; color: {status_color};'
            
            with col1:
                st.markdown(f'<div style="{heading_style}">Status</div>', unsafe_allow_html=True)
                status_text = job.get("status", "Unknown").capitalize()
                st.markdown(f'<div style="{content_style} font-weight: 500;">{status_text}</div>', unsafe_allow_html=True)
                
                # Get the raw timestamp
                raw_date = job.get("completion_timestamp") or job.get("process_timestamp")
                
                if raw_date and raw_date != "N/A":
                    # If your date_str is a single string like "2026-05-29 12:46:09"
                    # We can split it into Date and Time (assuming a space separator)
                    try:
                        date_part, time_part = str(raw_date).split(' ', 1)
                    except ValueError:
                        date_part, time_part = str(raw_date), ""

                    # Ensure we only show HH:MM:SS (the first 8 characters)
                    formatted_time = time_part[:8]

                    st.markdown(f"""
                        <div style="margin-top: 5px;">
                            <div style="font-size: 0.7rem; color: #71717a; line-height: 1.2;">
                                <strong>Processed Date:</strong> {date_part}
                            </div>
                            <div style="font-size: 0.7rem; color: #71717a; line-height: 1.2;">
                                <strong>Processed Time:</strong> {formatted_time}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown('<div style="font-size: 0.7rem; color: #71717a;">N/A</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<div style="{heading_style}">Dataset 1</div>', unsafe_allow_html=True)
                name = job.get("dataset1", "N/A")
                # Display name as plain text instead of a button
                st.markdown(f'<div style="{content_style}">{name}</div>', unsafe_allow_html=True)
                
                # Display the size below
                if job.get("size1"):
                    size_mb = round(job["size1"] / (1024 * 1024), 2)
                    st.markdown(f'<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">{size_mb} MB</div>', unsafe_allow_html=True)

            with col3:
                st.markdown(f'<div style="{heading_style}">Dataset 2</div>', unsafe_allow_html=True)
                name = job.get("dataset2", "N/A")
                # Display name as plain text
                st.markdown(f'<div style="{content_style}">{name}</div>', unsafe_allow_html=True)
                
                if job.get("size2"):
                    size_mb = round(job.get("size2", 0) / (1024 * 1024), 2)
                    st.markdown(f'<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">{size_mb} MB</div>', unsafe_allow_html=True)

            with col4:
                st.markdown(f'<div style="{heading_style}">Harmonized</div>', unsafe_allow_html=True)
                name = job.get("harmonized_filename", "N/A")
                # Display name as plain text
                st.markdown(f'<div style="{content_style}">{name}</div>', unsafe_allow_html=True)
                
                if job.get("harmonized_size"):
                    size_mb = round(job.get("harmonized_size", 0) / (1024 * 1024), 2)
                    st.markdown(f'<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">{size_mb} MB</div>', unsafe_allow_html=True)
            
            st.divider()
    else:
        st.info("No processing history yet")


def main():
    """Main application logic incorporating clean URL-driven navigation routers."""
    # Catch active URL parameters to switch views reliably without input conflict loops
    if "action" in st.query_params:
        action = st.query_params["action"]
        if action in ["login", "signup"] and st.session_state.auth_view != action:
            st.session_state.auth_view = action
            st.query_params.clear()
            st.rerun()

    if st.session_state.user_id is None:
        render_auth_page()
    else:
        render_sidebar()
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
            
        if st.session_state.current_page == 'dashboard':
            render_dashboard()
        elif st.session_state.current_page == 'history':
            render_history()


if __name__ == "__main__":
    main()