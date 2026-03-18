import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Updated CSS to match the exact alignment and dark theme
st.markdown("""
    <style>
    /* Global Dark Theme Background */
    .stApp {
        background-color: #0E1117;
    }

    /* Unified Dark Uploader Block */
    [data-testid="stFileUploader"] {
        background-color: #1E1F23 !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        padding: 60px 40px !important;
        text-align: center;
    }
    
    /* Center the internal uploader content */
    [data-testid="stFileUploader"] section {
        justify-content: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Positioning pills inside the block, above the "Drag & drop" text */
    .internal-pill-container {
        text-align: center;
        margin-bottom: -100px; /* Adjusts the vertical position inside the box */
        position: relative;
        z-index: 100;
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

    /* Validation Settings Dark Theme */
    .stExpander {
        background-color: #1E1F23 !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    label[data-testid="stWidgetLabel"] p {
        font-size: 13px !important;
        font-weight: bold !important;
        color: #E0E0E0 !important;
        text-transform: uppercase;
    }
    
    .stCaption {
        color: #808495 !important;
    }

    /* Right-aligned Royal Blue Button */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
        float: right;
        padding: 10px 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("NEW VALIDATION RUN")

# --- UPLOAD SECTION ---
st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# Column Pills Block (Word "Required columns" removed)
st.markdown("""
    <div class="internal-pill-container">
        <div>
            <span class="column-pill">audio_id</span>
            <span class="column-pill">speaker_A_audio</span>
            <span class="column-pill">speaker_B_audio</span>
            <span class="column-pill">combined_audio</span>
            <span class="column-pill">transcription</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Uploader
main_csv = st.file_uploader(
    "**Drag & drop your CSV file** or click to browse", 
    type=["csv"], 
    label_visibility="collapsed"
)

# --- VALIDATION SETTINGS ---
with st.expander("⚙️ Validation Settings", expanded=True):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        st.number_input("MIN DURATION (S)", value=1)
        st.markdown('<p class="stCaption">Minimum audio length</p>', unsafe_allow_html=True)
    with v_col2:
        st.number_input("MAX DURATION (S)", value=600)
        st.markdown('<p class="stCaption">Maximum audio length</p>', unsafe_allow_html=True)
    with v_col3:
        st.number_input("WER THRESHOLD", value=0.15)
        st.markdown('<p class="stCaption">Max WER to pass (0-1)</p>', unsafe_allow_html=True)
    with v_col4:
        st.number_input("CONCURRENCY", value=3)
        st.markdown('<p class="stCaption">Parallel rows (1-10)</p>', unsafe_allow_html=True)

# --- ACTION BUTTON ---
st.markdown("<br>", unsafe_allow_html=True)
btn_spacer, btn_col = st.columns([5, 1])
with btn_col:
    run_pressed = st.button("Start Validation", disabled=not main_csv)