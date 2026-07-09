"""
style_utils.py
--------------
Shared custom CSS: gradient dark theme (black -> mid gray), stretched
(wide letter-spacing) text, sidebar fully hidden (single-page app).
"""

import streamlit as st

CUSTOM_CSS = """
<style>
/* Gradient dark background: black -> mid gray */
.stApp {
    background: linear-gradient(160deg, #000000 0%, #1a1a1d 45%, #3a3a3f 100%);
}

/* Completely hide the sidebar and its collapse arrow */
section[data-testid="stSidebar"],
div[data-testid="collapsedControl"] {
    display: none !important;
}

/* Headings */
h1, h2, h3 {
    color: #ffffff !important;
    font-family: 'Trebuchet MS', sans-serif;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    text-align: center;
    margin-bottom: 0;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    word-spacing: 0.2em;
}

.hero-subtitle {
    text-align: center;
    color: #b8b8c0;
    font-size: 1.05rem;
    margin-top: 0.3rem;
    margin-bottom: 1.5rem;
    letter-spacing: 0.05em;
}

/* Detected gesture live banner */
.detected-banner {
    background: rgba(74, 222, 222, 0.08);
    border: 2px solid #4ADEDE;
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    font-size: 2rem;
    font-weight: 800;
    color: #4ADEDE;
    margin-top: 12px;
    letter-spacing: 0.15em;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    border: 1px solid #4ADEDE;
    color: white;
    background: #14141c;
    font-weight: 600;
    letter-spacing: 0.08em;
}

/* Toggle labels and captions */
label, .stMarkdown, .stCaption {
    color: #d0d0e0 !important;
    letter-spacing: 0.03em;
}
</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
