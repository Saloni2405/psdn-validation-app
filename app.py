import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Comprehensive CSS to match exactly the provided screenshots
st.markdown("""
    <style>
    /* 1. Start Validation Button - Right Aligned Royal Blue */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
        float: right;
    }

    /* 2. Enhanced & Centered Upload Block */
    [data-testid="stFileUploader"] {
        background-color: #1E1F23;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 60px 40px !important; /* Increased block size */
        text-align: center;
    }
    
    /* Center the internal content of the uploader */
    [data-testid="stFileUploader"] section {
        justify-content: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Column Pills integrated inside the block area */
    .pill-container {
        margin-top: -85px; /* Pulls pills into the visual block area */
        margin-bottom: 25px;
        position: relative;
        z-index: 10;
        text-align: center;
    }

    .column-pill {
        display: inline-block;
        background-color: #2D2E35;
        color: #E0E0E0;
        padding: 5px 14px;
        border-radius: 6px;
        margin: 4px;
        font-family: monospace;
        font-size: 13px;
        border: 1px solid #444;
    }

    .req-header {
        color: #808495;
        font-size: 14px;
        margin-bottom: 10px;
    }

    /* 3. Validation Settings Styling (Matches Screenshot 4.49.23 PM) */
    .stExpander {
        background-color: white !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        color: #333 !important;
    }
    
    /* Styling Number Input Labels and Help Text */
    label[data-testid="stWidgetLabel"] p {
        font-size: 13px !important;
        font-weight: bold !important;
        color: #5F6368 !important;
        text-transform: uppercase;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        font-size: 12px;
        color: #808495;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("NEW VALIDATION RUN")

# --- UPLOAD SECTION ---
st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# The Integrated Column Block (sitting inside the uploader area)
st.markdown("""
    <div class="pill-container">
        <div class="req-header">Required columns:</div>
        <div>
            <span class="column-pill">audio_id</span>
            <span class="column-pill">speaker_A_audio</span>
            <span class="column-pill">speaker_B_audio</span>
            <span class="column-pill">combined_audio</span>
            <span class="column-pill">transcription</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Uploader with centered text
main_csv = st.file_uploader(
    "**Drag & drop your CSV file** or click to browse", 
    type=["csv"], 
    label_visibility="collapsed"
)

# --- VALIDATION SETTINGS (Matches Screenshot Exactly) ---
#
with st.expander("⚙️ Validation Settings", expanded=True):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        st.number_input("MIN DURATION (S)", value=1)
        st.caption("Minimum audio length")
    with v_col2:
        st.number_input("MAX DURATION (S)", value=600)
        st.caption("Maximum audio length")
    with v_col3:
        st.number_input("WER THRESHOLD", value=0.15)
        st.caption("Max WER to pass (0-1)")
    with v_col4:
        st.number_input("CONCURRENCY", value=3)
        st.caption("Parallel rows (1-10)")

# --- ACTION BUTTON ---
btn_spacer, btn_col = st.columns([5, 1]) # Pushes button to the right
with btn_col:
    run_pressed = st.button("Start Validation", disabled=not main_csv)

# --- RUN LOGIC ---
if main_csv and run_pressed:
    st.write("---")
    st.success("Validation sequence started.")