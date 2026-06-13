"""
Streamlit application for Dataset Harmonization Pipeline
Frontend for uploading, processing, and downloading harmonized datasets
"""
import streamlit as st
import pandas as pd
import os
import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path
import json
from report_generator import generate_report
# Local asset paths
ROOT_DIR = Path(__file__).resolve().parent
LOGO_PATH = ROOT_DIR / "Logo" / "Logo.png"

# Import custom modules
from config import UPLOADS_DIR, OUTPUTS_DIR
from database import init_database, DB_PATH
from auth import register_user, login_user, get_user_info, user_exists
from db_utils import (
    save_upload_record, 
    get_user_uploads, 
    save_processing_record,
    update_processing_status, 
    save_download_record, 
    get_user_processing_history,
    get_user_download_history, 
    get_processing_details, 
    get_download_file_path,
    delete_user_account,    
    update_user_info        
)
from pipeline import run_pipeline

# Page configuration
st.set_page_config(
    page_title="Dataset Harmonization Platform",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Navigation is handled via the top navigation bar for logged-in users
# and via query parameters ("?page=...") to keep URL-driven routing.

def render_logo(size=120, centered=True):
    """Render app logo."""
    
    if not LOGO_PATH.exists():
        return

    # Default: centered logo (existing behavior)
    if centered:
        c1, c2, c3 = st.columns([4, 2, 3])
        with c2:
            st.image(str(LOGO_PATH), width=size)

    # Inline logo (for title row)
    else:
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
    /* Import a playful headline font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
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
    
    div[data-testid="stSelectbox"] {
        position: fixed;
        top: 10px;
        left: 20px;
        width: 250px;
        z-index: 9999;
    }

    div[data-testid="stSelectbox"] > div {
        background-color: #0f0f11;
        border: 1px solid #27272a;
        border-radius: 8px;
    }
            
    /* ===============================
    DISABLE SIDEBAR (we replace it)
    ================================= */
    div[data-testid="stSidebar"],
    div[data-testid="stSidebarContent"] {
        display: none !important;
    }
    div[data-testid="stMain"] {
    padding-left: 0rem !important;
    }
    div[data-testid="stAppViewContainer"] {
    padding-top: 40px;
    }
            
    /* Font Family Assignment */
    html, body, [data-testid="stAppViewContainer"] * {
        font-family: 'Quicksand', 'Inter', sans-serif !important;
    }
    
    /* Global page background and text styling */
    html, body, #root, .main, .block-container, div[data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #f8fbff !important;
        font-family: 'Quicksand', 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
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
        fill: #c48a6a !important;
        color: #c48a6a !important;
    }
    
    div[data-testid="stAppViewContainer"] {
        background: #000000 !important;
        background-attachment: fixed !important;
    }

    .top-nav {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: rgba(15, 15, 17, 0.96) !important;
        border-bottom: 1px solid #27272a;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 20px;
        z-index: 2147483647;
        gap: 10px;
        min-height: 46px;
        backdrop-filter: blur(14px);
    }

    .top-nav-links {
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
    }

    .top-nav-item {
        color: #e8f5e9;
        font-weight: 400;
        font-size: 0.92rem;
        text-decoration: none !important;
        padding: 6px 10px;
        border-radius: 8px;
        border: 1px solid transparent;
        transition: 0.2s ease;
    }

    .top-nav-item:hover,
    .top-nav-item.active {
        background-color: #17171b;
        color: #a7f3d0 !important;
        border-color: #3f3f46;
    }

    .page-title-spacer {
        height: 56px;
    }

    .top-nav-toggle,
    .top-nav-toggle-checkbox {
        display: none;
    }

    .top-nav-item:hover,
    .top-nav-toggle:hover {
        background-color: #1f1f23;
        color: #a7f3d0;
        border-color: #27272a;
    }

    .top-nav-item.active,
    .top-nav-item[aria-current="page"] {
        background-color: #1f1f23;
        color: #a7f3d0;
        font-weight: 600;
        border-color: #27272a;
    }

    .top-nav-toggle {
        display: none;
        width: 100%;
        justify-content: space-between;
    }

    .top-nav-toggle-checkbox {
        display: none;
    }

    @media (max-width: 880px) {
        .top-nav {
            align-items: stretch;
            flex-wrap: wrap;
            padding: 10px 16px;
        }

        .top-nav-toggle {
            display: inline-flex;
        }

        .top-nav-links {
            display: none;
            flex-direction: column;
            width: 100%;
            margin-top: 10px;
            background: #0f0f11;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 10px;
        }

        .top-nav-item {
            width: 100%;
        }

        .top-nav-toggle-checkbox:checked + .top-nav-toggle + .top-nav-links {
            display: flex;
        }
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
        margin-bottom: 1rem;
        font-size: 1.6rem !important;
        font-weight: 500;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg,#7ce7d9,#9b8cff,#ff6fa3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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
        background: linear-gradient(90deg,#7ce7d9,#ff9ec4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h3 {
        font-size: 1.3rem !important;
        background: linear-gradient(90deg,#9b8cff,#ff6fa3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Absolute Left-Aligned Custom Subheader Class for Auth Views */
    .auth-subheader {
        font-size: 1.6rem !important;
        font-weight: 500 !important;
        max-width: 430px !important;
        margin: -1.6rem auto 1.2rem auto !important;
        text-align: left !important;
        background: linear-gradient(90deg,#7ce7d9,#ff9ec4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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
        background-color: #000000 !important;
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
        margin: 0.75rem auto !important;
    }

    .stButton > button {
        background: linear-gradient(90deg,#5bb8aa 0%, #7a9ec9 50%, #8b78b8 100%) !important;
        color: #021112 !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.85rem 1rem !important;
        min-height: 44px !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button *, .stDownloadButton > button, .stDownloadButton > button * {
        color: #021112 !important;
        font-weight: 600 !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        opacity: 0.96 !important;
        box-shadow: 0 10px 24px rgba(91,184,170,0.12) !important;
    }

    /* Redirect Box alignment matching input structural boundaries */
    .redirect-box {
        max-width: 430px !important;
        margin: 1.5rem auto 0 auto !important;
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
    }

    .redirect-link {
        color: #021112 !important;
        text-decoration: none !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        background: linear-gradient(90deg,#5bb8aa 0%, #7a9ec9 50%, #8b78b8 100%) !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 430px;
        padding: 0.85rem 1rem;
        border-radius: 999px;
        box-shadow: 0 10px 24px rgba(91,184,170,0.12);
        cursor: pointer;
        margin: 0 auto !important;
    }
    
    .redirect-link:hover {
        opacity: 0.95 !important;
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

st.markdown("""
    <style>
    /* Reduce the default top padding of the main content block */
    .stMainBlockContainer {
        padding-top: 2rem !important;
    }
    
    /* Optional: Add a small gap between the fixed top nav and page headings */
    .main-header {
        margin-top: 1rem !important;
        margin-bottom: 1.8rem !important;
    }
    
    /* Pull navigation buttons higher */
    [data-testid="stHorizontalBlock"] {
        margin-top: -3.2rem !important;
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
    st.session_state.auth_view = None  # None means show landing page


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


def resolve_existing_path(file_path):
    if not file_path:
        return None
    path = Path(file_path)
    candidates = [path]
    if not path.is_absolute():
        candidates.append(ROOT_DIR / path)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def read_download_bytes(file_path):
    path = resolve_existing_path(file_path)
    return path.read_bytes() if path else None


def render_auth_page():
    """Render unified seamless login and signup views cleanly styled."""
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0.3rem;
            }
        </style>
    """, unsafe_allow_html=True)
    # MOVE LOGO CALLS HERE: This ensures it renders before the title
    render_logo(size=120)
    
    # Inject a clean anchor element
    st.markdown("<div class='auth-card-anchor'></div>", unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.auth_view == 'login':
        
            st.markdown("<div class='auth-subheader'>Login</div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            validation_error = st.empty()
            # Local CSS for Sign Up button text
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button span,
            div[data-testid="stButton"] > button p {
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button("Login", use_container_width=True):
                if username and password:
                    success, user_id, message = login_user(username, password)
                    if success:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.session_state.logged_in = True
                        st.session_state.current_page = 'home'
                        # Mark as a returning login (not a fresh signup)
                        st.session_state.just_signed_up = False
                        st.session_state.auth_view = None
                        st.success(f"✅ Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    validation_error.warning("⚠️ Oops, you haven't filled everything in!")
            
            st.markdown("""
                <div class='redirect-box'>
                    <a href='?action=signup' class='redirect-link'>
                        Don't have an account? Sign up here!
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

            # Local CSS for Back button text
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button span,
            div[data-testid="stButton"] > button p {
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button("Back", use_container_width=True):
                st.session_state.auth_view = None
                st.rerun()
        
        elif st.session_state.auth_view == 'signup':
            st.markdown("<div class='auth-subheader'>Sign Up</div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="signup_username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            validation_error = st.empty()
            # Local CSS for Sign Up button text
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button span,
            div[data-testid="stButton"] > button p {
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button("Sign Up", use_container_width=True):
                if not (username and email and password and confirm_password):
                    validation_error.warning("⚠️ Oops, you haven't filled everything in!")
                elif password != confirm_password:
                    st.error("Passwords don't match")
                else:
                    success, message = register_user(username, email, password)
                    if success:
                        # Instead of fetching a DB ID, we use the username as the unique identifier
                        st.session_state.user_id = username 
                        st.session_state.username = username
                        st.session_state.logged_in = True
                        st.session_state.current_page = 'home'
                        
                        # Clearing auth_view signals the main loop that the user is logged in
                        st.session_state.auth_view = None 
                        # Signal that this session was created by a fresh signup
                        st.session_state.just_signed_up = True
                        st.success(f"✅ Account created! Redirecting...")
                        st.rerun() 
                    else:
                        st.error(f"❌ {message}")
            
            st.markdown("""
                <div class='redirect-box'>
                    <a href='?action=login' class='redirect-link'>
                        Already have an account? Log in here!
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)

            # Local CSS for this Back button
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button span,
            div[data-testid="stButton"] > button p {
                color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button("Back", use_container_width=True):
                st.session_state.auth_view = None
                st.rerun()


def render_landing_page(): 
    """Render the opening landing page before login/signup.""" 
    st.markdown("""
        <style> 
            .landing-container {
                max-width: 860px; 
                margin: 0 auto; 
                padding: 3.5rem 1.25rem 2.5rem; 
                text-align: center; 
            } 
            .landing-header {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 18px;
                margin-bottom: 0.8rem;
            }

            .landing-logo img {
                width: 90px;
                height: 90px;
                object-fit: contain;
            }
            .landing-title { 
                font-size: 3.2rem; 
                color: #ffd6e8; 
                margin: 0 0 0.6rem; 
                letter-spacing: 0.02em; 
                font-family: 'Quicksand', 'Inter', sans-serif !important; 
                font-weight: 500; 
                background: linear-gradient(90deg,#7ce7d9,#9b8cff,#ff6fa3); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
            } 
            .landing-tagline { 
                color: #f1f5f9; 
                font-size: 1.08rem; 
                line-height: 1.7; 
                margin: 0 auto 1rem; 
                max-width: 680px; 
                font-family: 'Quicksand', 'Inter', sans-serif !important; 
                font-weight: 300; 
            } /* small about link fixed to top-right on the landing page only */ 
            .landing-about-button { 
                display: inline-flex; 
                align-items: center; 
                justify-content: center; 
                margin: 0.6rem auto 0.6rem; 
                padding: 0.85rem 1.4rem; 
                border-radius: 999px; background: 
                linear-gradient(90deg,#7ce7d9 0%, #ff9ec4 50%, #9b8cff 100%); 
                color: #061018; 
                text-decoration: none; 
                font-size: 1.05rem; 
                font-weight: 600; 
                box-shadow: 0 14px 30px rgba(155,140,255,0.12); 
                transition: transform 0.15s ease, opacity 0.15s ease; 
                border: 1px solid rgba(255,255,255,0.04); 
            } 
            .landing-about-button:hover { 
                transform: translateY(-2px); opacity: 0.98; 
            } 
            .landing-links { 
                display: inline-flex; 
                gap: 12px; 
                flex-wrap: wrap; 
                justify-content: center; 
                margin-top: 0.6rem; 
            } 
            .landing-link { 
                color: #021112; 
                border: 1px solid rgba(255,255,255,0.06); 
                padding: 0.85rem 1rem; 
                border-radius: 999px; 
                text-decoration: none; 
                font-size: 0.95rem; 
                font-weight: 600; 
                transition: all 0.15s ease; 
                background: linear-gradient(90deg,#5bb8aa 0%, #7a9ec9 50%, #8b78b8 100%); 
                box-shadow: 0 10px 24px rgba(91,184,170,0.08); 
            } 
            .landing-link:hover { 
                background-color: #121018; 
                border-color: #7c3aed; 
                color: #f8f4ff; } 
        </style> 
    """, unsafe_allow_html=True) 
     
    import base64
    from pathlib import Path

    def get_base64_image(image_path):
        with open(image_path, "rb") as img:
            return base64.b64encode(img.read()).decode()

    logo_base64 = get_base64_image(LOGO_PATH)

    st.markdown(f""" 
        <div class='landing-container'> 
            <div class='landing-header'>
                <div class='landing-logo'>
                    <img src="data:image/png;base64,{logo_base64}" />
                </div>
                <div class='landing-title'>Syncify</div>
            </div> 
            <div class='landing-tagline'>A smart dataset harmonization tool that aligns columns, merges data, and produces clean outputs for analysis.<br/>Fast, visual, and easy to use.</div> 
                <a class='landing-about-button' href='?action=about' target='_self'>About Syncify</a> 
            <div style='height:8px;'></div> 
            <div class='landing-links'> 
                <a class='landing-link' href='?action=signup' target='_self'>Don't have an account? Sign in!</a> 
                <a class='landing-link' href='?action=login' target='_self'>Already have an account? Login!</a> 
            </div> 
        </div> 
    """, unsafe_allow_html=True)


def render_about_page():
    """Render the About page for the app."""

    import base64
    from pathlib import Path

    def get_base64_image(image_path):
        with open(image_path, "rb") as img:
            return base64.b64encode(img.read()).decode()

    logo_base64 = get_base64_image(LOGO_PATH)
    
    st.markdown(f"""
        <div style="
            display: flex;
            justify-content: center;
            margin-top: 1.2rem;
            margin-bottom: 0.4rem;
        ">
            <img src="data:image/png;base64,{logo_base64}"
                style="width:80px; height:80px; object-fit:contain;">
        </div>
    """, unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size: 2.5rem;">
            <h1 class='main-header' style='font-size: inherit !important;'>About Syncify</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        <div class='info-box'>
            <p style='margin:0 0 0.9rem; font-size:1rem; color:#e8f5e9;'><strong>✨ Syncify</strong> is your data sidekick! It brings multiple datasets together into one sparkly, harmonized output. No more tedious column matching — let Syncify handle the heavy lifting so you can focus on insights!</p>
            <p style='margin:0; color:#c4fffd;'>Built for speed, clarity, and keeping your data organized. Your sync partner for perfectly aligned datasets! </p>
        </div>
        <div style='margin-top:1rem;'>
            <h3 style='font-size:1.05rem; margin-bottom:0.45rem;'>🎯 Why Syncify was created</h3>
            <p style='color:#f0f9ff; line-height:1.6;'>Data harmonization was feeling like a chore—lots of manual matching, endless clicking, and tiny mistakes creeping in. We built Syncify to transform that headache into a joy! One click. Clean data. Your time back.</p>
        </div>
        <div style='margin-top:0.9rem;'>
            <h3 style='font-size:1.05rem; margin-bottom:0.45rem;'>⚙️ How Syncify was built</h3>
            <p style='color:#f0f9ff; line-height:1.6;'>A lightweight Python powerhouse with a Streamlit frontend that feels buttery smooth. <strong>pandas</strong> does the data wizardry, <strong>SQLite</strong> keeps your history safe and sound, and modular Python scripts tie it all together like a dream.</p>
        </div>
        <div style='margin-top:0.9rem;'>
            <h3 style='font-size:1.05rem; margin-bottom:0.45rem;'>🛠️ Tech stack & libraries</h3>
            <ul style='color:#f0f9ff; line-height:1.6; padding-left:1.1rem;'>
                <li><strong>Streamlit</strong> — sleek, responsive UI </li>
                <li><strong>pandas</strong> — data transformation magic </li>
                <li><strong>SQLite</strong> — your secure data vault </li>
                <li><strong>python-docx</strong> — beautiful report generation </li>
            </ul>
        </div>
        <div style='margin-top:0.9rem;'>
            <h3 style='font-size:1.05rem; margin-bottom:0.45rem;'>🚀 How to use Syncify</h3>
            <ul style='color:#f0f9ff; line-height:1.8; padding-left:1.1rem;'>
            <li><strong>Step 1:</strong> Create your account or log in.</li>
            <li><strong>Step 2:</strong> Upload two datasets and watch the magic happen.</li>
            <li><strong>Step 3:</strong> Review the matches and harmonize with confidence.</li>
            <li><strong>Step 4:</strong> Download your harmonized dataset and report. </li>
        </ul>
        </div>
        <div style='margin-top:0.9rem;'>
            <h3 style='font-size:1.05rem; margin-bottom:0.45rem;'>🔒 Security & privacy</h3>
            <ul style='color:#f0f9ff; line-height:1.6; padding-left:1.1rem;'>
                <li>Your data is yours alone. Secure login means only you see your datasets.</li>
                <li>Encrypted storage in a local SQLite vault — ultra-safe, ultra-fast.</li>
                <li>Passwords protected with industry-standard hashing. Deploy behind HTTPS for extra peace of mind.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Only show Back button if NOT logged in (when accessed from landing page)
    st.markdown("""
    <style>
    /* Back button text */
    div.stButton > button {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* Streamlit often puts text inside span */
    div.stButton > button span {
        color: #000000 !important;
    }

    /* Some versions use p tags */
    div.stButton > button p {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if not st.session_state.get("logged_in", False):
        st.markdown("<div style='margin-top:1.5rem; text-align:center;'></div>", unsafe_allow_html=True)
        if st.button("Back", use_container_width=True):
            st.query_params.clear()
            st.rerun()


def render_sidebar():
    """Render the top navigation menu for logged-in users."""
    if not st.session_state.get("logged_in", False):
        return

    current_page = st.session_state.get("current_page", "home")
    nav_items = [
        ("About", "about"),
        ("Home", "home"),
        ("Harmonizer", "dashboard"),
        ("History", "history"),
        ("Profile", "profile"),
    ]
    # Use Streamlit buttons in a horizontal row to ensure clicks are handled
    # We'll render equal-width buttons using columns and CSS classes for spacing
    cols = st.columns(len(nav_items) + 1)
    for i, (label, page) in enumerate(nav_items):
        with cols[i]:
            clicked = st.button(label, key=f"nav_{page}")
            if clicked:
                st.session_state.current_page = page
                try:
                    st.query_params = {"page": page}
                except Exception:
                    try:
                        st.experimental_set_query_params(page=page)
                    except Exception:
                        pass
                st.rerun()

    # Logout button at the end
    with cols[-1]:
        if st.button("Logout", key="nav_logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.logged_in = False
            st.session_state.auth_view = 'login'
            st.session_state.just_signed_up = False
            try:
                st.query_params = {"do": "logout"}
            except Exception:
                try:
                    st.experimental_set_query_params(do='logout')
                except Exception:
                    pass
            st.rerun()

    # Add style tweak so the buttons are equal width and spaced
    st.markdown("""
        <style>
            /* Equal width buttons */
            .stButton > button {
                width: 100% !important;
                color: #000000 !important;
            }

            /* Button text inside span/p tags */
            .stButton > button span,
            .stButton > button p {
                color: #000000 !important;
            }

            /* Spacing between nav buttons */
            .css-1j6p8o2 {
                gap: 8px !important;
            }
        </style>
        """, unsafe_allow_html=True)

def render_home():
    """Render the Home page with welcome messaging and recent activity."""
    st.markdown(
        """
        <div style="font-size: 2.5rem;">
            <h1 class='main-header' style='font-size: inherit !important;'>Home</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    processing_history = []
    try:
        processing_history = get_user_processing_history(st.session_state.user_id)
    except Exception:
        processing_history = []

    is_new_signup = st.session_state.get('just_signed_up', False)
    if is_new_signup:
        st.markdown("""
            <div style='padding:12px; border-radius:8px; background:#0f0f11;'>
                <h3 style='color:#e1b995;margin:0;'>Welcome! Start using Data Harmonizer!</h3>
                <p style='color:#94a3b8;margin-top:0.8rem; font-size:0.95rem;'>Your dashboard is ready. Upload datasets and harmonize them with a few clicks.</p>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.just_signed_up = False
    else:
        st.markdown("""
            <div style='padding:12px; border-radius:8px; background:#0f0f11;'>
                <h3 style='color:#e1b995;margin:0;'>Welcome back!</h3>
                <p style='color:#94a3b8;margin-top:0.8rem; font-size:0.95rem;'>Continue where you left off and keep your harmonization process moving.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin-top:1.25rem;'>✨ Recent Activity</h3>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:3rem;'></div>", unsafe_allow_html=True)

    if processing_history:
        recents = processing_history[:3]
        cols = st.columns(len(recents))
        for col, job in zip(cols, recents):
            name = job.get('harmonized_filename') or 'Unnamed Harmonized Dataset'
            report = job.get('report_filename') or 'No report'
            with col:
                st.markdown(f"""
                    <div style='border:1px solid #222226;padding:12px;border-radius:8px;width:100%;margin-top:0.6rem;box-sizing:border-box;word-break:break-word;'>
                        <div style='font-weight:600;color:#e8f5e9'>{name}</div>
                        <div style='color:#e8f5e9;margin-top:6px'>{report}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        message = "No activity yet!" if is_new_signup else "No recent activity!"
        st.markdown(f"<div style='color:#94a3b8; font-size:0.95rem; margin-top:0.75rem;'>{message}</div>", unsafe_allow_html=True)


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
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="font-size: 2.5rem;">
            <h1 class='main-header' style='font-size: inherit !important;'>Harmonizer</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 2. File Upload Section
    st.markdown("""
    <h3 style="display: flex; align-items: center; gap: 10px; color: #e1b995 !important;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e1b995" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 13V3l4 4M12 3L8 7M6 13v6a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-6"/>
        </svg>
        Upload Datasets
    </h3>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Dataset 1**")
        # The CSS we added earlier will automatically style this uploader
        file1 = st.file_uploader("Choose first dataset", key="file1", type=['csv', 'xlsx', 'xls'])
    with col2:
        st.markdown("**Dataset 2**")
        file2 = st.file_uploader("Choose second dataset", key="file2", type=['csv', 'xlsx', 'xls'])

    current_upload_signature = (
        (file1.name, file1.size) if file1 else None,
        (file2.name, file2.size) if file2 else None
    )
    latest_result = st.session_state.get("latest_harmonization_result")
    if (
        latest_result
        and any(current_upload_signature)
        and latest_result.get("input_signature") != current_upload_signature
    ):
        st.session_state.pop("latest_harmonization_result", None)
    
    st.markdown("<div style='margin-top: 0.9rem;'></div>", unsafe_allow_html=True)

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
        default_name = f"{os.path.splitext(file1.name)[0]}_{os.path.splitext(file2.name)[0]}"
        
       # 2. UI inputs for naming and format
        user_filename = st.text_input(
            "Filename for your harmonized dataset:", 
            value=default_name,
            key="harmonized_name_input"  # This key is required for the auto-focus script
        )
        
        output_format = st.radio("Select output format:", ["CSV", "Excel"], horizontal=True)

        if st.button("Harmonize!", use_container_width=True):
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
                    start_time = time.perf_counter()
                    pipeline_result = run_pipeline([file1_path, file2_path])
                    processing_seconds = time.perf_counter() - start_time

                    harmonized_outputs = pipeline_result["harmonized_outputs"]
                    datasets = pipeline_result["datasets"]

                    combined_df = pd.concat(
                        harmonized_outputs.values(),
                        ignore_index=True
                    )

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
                    
                    # Generate Word report with the same base name as the harmonized dataset.
                    report_filename = f"{os.path.splitext(download_filename)[0]} Report.docx"
                    report_path = generate_report(
                        combined_df,
                        file1.name,
                        file2.name,
                        datasets=datasets,
                        mappings=pipeline_result.get("mappings", {}),
                        reasonings=pipeline_result.get("reasonings", {}),
                        output_dataset_name=download_filename,
                        output_dataset_path=str(output_path),
                        report_filename=report_filename,
                        processing_seconds=processing_seconds
                    )

                    # 5. Finalize Records and Cleanup
                    file_size_bytes = os.path.getsize(output_path)

                    save_download_record(
                        st.session_state.user_id,
                        process_id,
                        download_filename,
                        str(output_path),
                        file_size_bytes
                    )

                    update_processing_status(
                        process_id,
                        'Completed',
                        None,
                        {
                            'name': download_filename,
                            'path': str(output_path),
                            'size': file_size_bytes,
                            'report_filename': report_filename,
                            'report_path': str(report_path)
                        }
                    )

                    st.session_state.latest_harmonization_result = {
                        "row_count": len(combined_df),
                        "column_count": len(combined_df.columns),
                        "output_path": str(output_path),
                        "download_filename": download_filename,
                        "mime_type": mime_type,
                        "output_format": output_format,
                        "report_path": str(report_path),
                        "report_filename": report_filename,
                        "input_signature": current_upload_signature
                    }

                    st.success("✅ Harmonization completed successfully!")
                    
                except Exception as e:
                    if 'process_id' in locals():
                        update_processing_status(process_id, 'Failed', str(e))
                    st.error(f"❌ Error during processing: {str(e)}")

        latest_result = st.session_state.get("latest_harmonization_result")

        st.markdown("""
        <style>
        /* Download buttons */
        div[data-testid="stDownloadButton"] > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #52525b !important;
            font-weight: bold !important;
            border-radius: 5px !important;
            transition: all 0.2s ease-in-out !important;
            width: 100% !important;
        }

        /* Hover effect */
        div[data-testid="stDownloadButton"] > button:hover {
            background-color: #71717a !important;
            color: #FFFFFF !important;
            border: 1px solid #a1a1aa !important;
            box-shadow: 0 0 8px rgba(161, 161, 170, 0.5) !important;
        }

        /* Text inside button */
        div[data-testid="stDownloadButton"] > button span,
        div[data-testid="stDownloadButton"] > button p {
            color: #FFFFFF !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if latest_result:
            file_data = read_download_bytes(latest_result["output_path"])

            if file_data is not None:
                st.download_button(
                    label=f"Download {latest_result['output_format']} Dataset",
                    data=file_data,
                    file_name=latest_result["download_filename"],
                    mime=latest_result["mime_type"],
                    key="latest_harmonized_download",
                    on_click="ignore",
                    use_container_width=True
                )
            else:
                st.warning("Harmonized dataset file not found")

            st.subheader("Harmonization Report")
            report_data = read_download_bytes(latest_result["report_path"])
            if report_data is not None:
                st.success("Report generated successfully")
                st.download_button(
                    label="Download Report",
                    data=report_data,
                    file_name=latest_result["report_filename"],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="latest_report_download",
                    on_click="ignore",
                    use_container_width=True
                )
            else:
                st.warning("Report not found")


def render_history():
    """Render history page with consistent coloring across all columns."""
    st.markdown(
        """
        <div style="font-size: 2.5rem;">
            <h1 class='main-header' style='font-size: inherit !important;'>History</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    
    processing_history = get_user_processing_history(st.session_state.user_id)

    if processing_history:
        status_colors = {'Completed': '#22c55e', 'Processing': '#3b82f6', 'Failed': '#ef4444', 'Pending': '#a1a1aa'}
        
        for job in processing_history:
            # Determine the color based on job status
            status_color = status_colors.get(job.get('status'), '#a1a1aa')
            col1, col2, col3, col4, col5 = st.columns([0.8, 0.8, 0.8, 1.6, 1.6])
            
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
                st.markdown(
                    f'<div style="{content_style}">{name}</div>',
                    unsafe_allow_html=True
                )

                if job.get("size1"):
                    size_mb = round(job["size1"] / (1024 * 1024), 2)
                    st.markdown(
                        f'<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">{size_mb} MB</div>',
                        unsafe_allow_html=True
                    )


            with col3:
                st.markdown(f'<div style="{heading_style}">Dataset 2</div>', unsafe_allow_html=True)

                name = job.get("dataset2", "N/A")
                st.markdown(
                    f'<div style="{content_style}">{name}</div>',
                    unsafe_allow_html=True
                )

                if job.get("size2"):
                    size_mb = round(job.get("size2", 0) / (1024 * 1024), 2)
                    st.markdown(
                        f'<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">{size_mb} MB</div>',
                        unsafe_allow_html=True
                    )

            with col4:
                st.markdown(f'<div style="{heading_style}">Harmonized</div>', unsafe_allow_html=True)

                name = job.get("harmonized_filename", "N/A")
                st.markdown(
                    f'<div style="{content_style}">{name}</div>',
                    unsafe_allow_html=True
                )

                if job.get("harmonized_size"):
                    size_mb = round(job.get("harmonized_size", 0) / (1024 * 1024), 2)
                    st.markdown(
                        f'<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">{size_mb} MB</div>',
                        unsafe_allow_html=True
                    )


            with col5:
                st.markdown(f'<div style="{heading_style}">Report</div>', unsafe_allow_html=True)

                name = job.get("report_filename", "N/A")
                st.markdown(
                    f'<div style="{content_style}">{name}</div>',
                    unsafe_allow_html=True
                )

                if job.get("report_path"):
                    try:
                        size_mb = round(
                            os.path.getsize(job["report_path"]) / (1024 * 1024),
                            2
                        )
                        st.markdown(
                            f'<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">{size_mb} MB</div>',
                            unsafe_allow_html=True
                        )
                    except:
                        st.markdown(
                            '<div style="font-size: 0.65rem; color: #71717a; margin-top: 2px;">N/A</div>',
                            unsafe_allow_html=True
                        )
            st.markdown(
                "<hr style='margin: 0.8rem 0; border: none; border-top: 1px solid #27272a;'>",
                unsafe_allow_html=True
            )

            st.markdown("<div style='margin-bottom:3rem;'></div>", unsafe_allow_html=True)
    else:
        st.info("No processing history yet")


def render_settings():

    st.markdown("""
    <style>
    /* CSS for standard buttons */
    div.stFormSubmitButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #52525b !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stFormSubmitButton > button:hover {
        background-color: #71717a !important;
        color: #FFFFFF !important;
        border: 1px solid #a1a1aa !important;
        box-shadow: 0 0 8px rgba(161, 161, 170, 0.5) !important;
    }

    /* CSS to force left alignment */
    .left-align-btn {
        display: flex;
        justify-content: flex-start;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="font-size: 2.5rem;">
            <h1 class='main-header' style='font-size: inherit !important;'>Profile</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='margin-top: -1.4rem;'></div>", unsafe_allow_html=True)
    
    # Display basic account info at the top of the Profile page
    user_info = get_user_info(st.session_state.user_id)
    username_display = st.session_state.get('username', 'User')
    email_display = user_info.get('email', 'N/A') if user_info else 'N/A'
    created_display = None
    if user_info:
        created_at = user_info.get('created_at')
        if created_at:
            created_display = str(created_at).split(' ')[0]

    st.markdown(f"<div style='margin-bottom:12px'><strong>Username:</strong> {username_display} &nbsp;&nbsp; <strong>Email:</strong> {email_display} &nbsp;&nbsp; <strong>Created:</strong> {created_display or 'N/A'}</div>", unsafe_allow_html=True)

    # 1. Profile Management Section
    st.subheader("Edit Profile")
    with st.form("profile_form"):
        user_info = get_user_info(st.session_state.user_id)
        email_val = user_info.get("email", "") if user_info else ""
        
        new_username = st.text_input("New Username", value=st.session_state.username)
        new_email = st.text_input("New Email", value=email_val)
        
        st.markdown("### Change Password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("✏️ Update Profile", type="primary"):
            # Validation logic
            if "@" not in new_email:
                st.error("Please enter a valid email address.")
            elif new_password and new_password != confirm_password:
                st.error("Passwords don't match!")
            else:
                # Prepare data
                # Note: Pass None or empty string if user didn't type a new password
                password_to_update = new_password if new_password else None
                
                # Call your backend update function
                # Make sure your update_user_info function is updated to accept 'password'
                if update_user_info(st.session_state.user_id, new_username, new_email, password_to_update):
                    st.session_state.username = new_username
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile.")

    st.markdown("---")
    
    # 2. Danger Zone Section
    st.subheader("Account Deletion")
    st.write("⚠️ Deleting your account will permanently remove all your upload history, processing history, and downloaded files from our server.")
    
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False

    # Button wrapped in a div to force left-alignment
    st.markdown('<div class="left-align-btn">', unsafe_allow_html=True)
    if st.button("Delete My Account"):
        st.session_state.show_delete_confirm = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_delete_confirm:
        confirm = st.checkbox("I understand that this action cannot be undone and will delete all my data.")
        
        if confirm:
            if st.button("💀 Confirm Permanent Delete", type="primary"):
                if delete_user_account(st.session_state.user_id):
                    st.success("Account deleted successfully.")
                    st.session_state.clear()
                    st.rerun() 
                else:
                    st.error("Error occurred while deleting account.")
        
        if st.button("❌ Cancel"):
            st.session_state.show_delete_confirm = False
            st.rerun()

def main():
    """Main application logic incorporating clean URL-driven navigation routers."""
    
    # URL-driven actions (login/signup/about) are handled further down
    
    # Handle explicit logout action (only this triggers logout)
    if "do" in st.query_params:
        raw_do = st.query_params.get("do")
        dos = list(raw_do) if isinstance(raw_do, (list, tuple)) else [raw_do]
        if any(d == "logout" for d in dos):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.logged_in = False
            st.session_state.auth_view = 'login'
            st.session_state.just_signed_up = False
            st.query_params.clear()

    # Render based on login state
    if st.session_state.user_id is None:

        # FIRST: Handle URL-driven actions
        if "action" in st.query_params:
            raw_action = st.query_params.get("action")
            action = raw_action[0] if isinstance(raw_action, (list, tuple)) else raw_action

            if action == "about":
                render_about_page()
                return

            if action in ["login", "signup"]:
                st.session_state.auth_view = action
                st.query_params.clear()
                render_auth_page()
                return

        # THEN: Preserve auth state
        if st.session_state.auth_view in ["login", "signup"]:
            render_auth_page()
            return

        render_landing_page()
    else:
        if "page" in st.query_params:
            raw_page = st.query_params.get("page")
            page = raw_page[0] if isinstance(raw_page, (list, tuple)) else raw_page
            if page in ["about", "home", "dashboard", "history", "profile"]:
                st.session_state.current_page = page
            st.query_params.clear()

        if "do" in st.query_params:
            raw_do = st.query_params.get("do")
            dos = list(raw_do) if isinstance(raw_do, (list, tuple)) else [raw_do]
            if any(d == "logout" for d in dos):
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.logged_in = False
                st.session_state.auth_view = None
                st.session_state.just_signed_up = False
                st.query_params.clear()
                st.rerun()
                return

        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'

        render_sidebar()

        if st.session_state.current_page == 'home':
            render_home()
        elif st.session_state.current_page == 'dashboard':
            render_dashboard()
        elif st.session_state.current_page == 'history':
            render_history()
        elif st.session_state.current_page == 'profile':
            render_settings()
        elif st.session_state.current_page == 'about':
            render_about_page()


if __name__ == "__main__":
    main()
