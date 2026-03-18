import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Comprehensive CSS for unified UI and specific element alignment
st.markdown("""
    <style>
    /* 1. Start Validation Button - Royal Blue & Right Aligned */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
        float: right; /* Forces right alignment within its column */
    }
    
    /* 2. Unified Uploader Block (Dark Theme) */
    [data-testid="stFileUploader"] {
        background-color: #262730;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 40px 20px 20px 20px;
    }

    /* Positioning columns inside the uploader box */
    .merged-container {
        position: relative;
        top: 75px; 
        z-index: 100;
        text-align: center;
        pointer-events: none; /* Allows clicks to pass through to the uploader */
    }

    .column-pill {
        display: inline-block;
        background-color: #31333F;
        color: #E0E0E0;
        padding: 4px 12px;
        border-radius: 5px;
        margin: 0 4px;
        font-family: monospace;
        font-size: 12px;
        border: 1px solid #555;
    }

    .req-text {
        color: #808495;
        font-size: 13px;
        margin-bottom: 8px;
    }

    /* 3. Validation Settings Styling (Matching Reference Image) */
    .stExpander {
        border: 1px solid #e6e9ef !important;
        border-radius: 10px !important;
    }
    
    /* Helper for number input labels to look like the image */
    label[data-testid="stWidgetLabel"] p {
        font-size: 12px !important;
        font-weight: bold !important;
        color: #5f6368 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("NEW VALIDATION RUN")

# --- UPLOAD SECTION ---
st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# Unified internal label block
st.markdown("""
    <div class="merged-container">
        <div class="req-text">Required columns:</div>
        <div>
            <span class="column-pill">audio_id</span>
            <span class="column-pill">speaker_A_audio</span>
            <span class="column-pill">speaker_B_audio</span>
            <span class="column-pill">combined_audio</span>
            <span class="column-pill">transcription</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

main_csv = st.file_uploader("", type=["csv"], label_visibility="collapsed")

# --- VALIDATION SETTINGS (Below Upload) ---
# Matches your Screenshot 4.49.23 PM
with st.expander("⚙️ Validation Settings", expanded=True):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    v_col1.number_input("MIN DURATION (S)", value=1, help="Minimum audio length")
    v_col2.number_input("MAX DURATION (S)", value=600, help="Maximum audio length")
    v_col3.number_input("WER THRESHOLD", value=0.15, help="Max WER to pass (0-1)")
    v_col4.number_input("CONCURRENCY", value=3, help="Parallel rows (1-10)")

# --- ACTION BUTTON ---
# Using a 4:1 column split to ensure the button is at the far right
btn_spacer, btn_col = st.columns([4, 1])
with btn_col:
    run_pressed = st.button("Start Validation", disabled=not main_csv)

# --- PROCESSING LOGIC ---
if main_csv and run_pressed:
    st.write("---")
    st.success("Validation sequence initiated...")