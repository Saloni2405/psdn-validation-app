import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Custom CSS for the "Complete Block" and layout
st.markdown("""
    <style>
    /* Royal Blue Button */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
    }
    
    /* The Uploader Box */
    [data-testid="stFileUploader"] {
        background-color: #262730;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 30px 20px 10px 20px;
    }

    /* Moving Labels inside the box using negative margin */
    .merged-labels {
        position: relative;
        top: 65px; /* Adjusts the vertical position inside the box */
        z-index: 99;
        text-align: center;
    }

    .column-tag {
        display: inline-block;
        background-color: #31333F;
        color: #E0E0E0;
        padding: 4px 12px;
        border-radius: 5px;
        margin: 5px;
        font-family: monospace;
        font-size: 12px;
        border: 1px solid #555;
    }

    .label-header {
        color: #808495;
        font-size: 13px;
        margin-bottom: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. HEADER ---
st.title("NEW VALIDATION RUN")

# --- 2. UPLOAD SECTION (Now First) ---
st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# The Merged Complete Block
st.markdown('<div class="merged-labels"><div class="label-header">Required columns:</div>', unsafe_allow_html=True)
st.markdown("""
        <div>
            <span class="column-tag">audio_id</span>
            <span class="column-tag">speaker_A_audio</span>
            <span class="column-tag">speaker_B_audio</span>
            <span class="column-tag">combined_audio</span>
            <span class="column-tag">transcription</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

main_csv = st.file_uploader("", type=["csv"], label_visibility="collapsed")

# --- 3. SETTINGS SECTION (Now Second) ---
with st.expander("⚙️ Validation Settings"):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    v_col1.number_input("MIN DURATION (S)", value=1)
    v_col2.number_input("MAX DURATION (S)", value=600)
    v_col3.number_input("WER THRESHOLD", value=0.15)
    v_col4.number_input("CONCURRENCY", value=3)

# Start Button
_, col_btn = st.columns([4, 1])
with col_btn:
    run_pressed = st.button("Start Validation", disabled=not main_csv)

# --- 4. RESULTS LOGIC ---
if main_csv is not None and run_pressed:
    st.write("---")
    # Metric data (191/196) and results go here...
    st.success("Analysis complete.")