import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Updated CSS to merge labels into the native uploader box
st.markdown("""
    <style>
    /* Royal Blue Button */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
    }
    
    /* Target the Streamlit Uploader Box to add space for our labels */
    [data-testid="stFileUploader"] {
        background-color: #262730; /* Match Streamlit dark theme */
        border: 1px solid #444;
        border-radius: 10px;
        padding-top: 20px;
    }

    /* Style for the column pills - No white background anymore */
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

    .label-text {
        color: #808495;
        font-size: 14px;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("NEW VALIDATION RUN")

# Validation Settings Dropdown
with st.expander("⚙️ Validation Settings"):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    v_col1.number_input("MIN DURATION (S)", value=1)
    v_col2.number_input("MAX DURATION (S)", value=600)
    v_col3.number_input("WER THRESHOLD", value=0.15)
    v_col4.number_input("CONCURRENCY", value=3)

st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# --- MERGED BLOCK ---
# We use a container to keep the labels and uploader physically together
with st.container():
    st.markdown('<div style="text-align: center;" class="label-text">Required columns:</div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; margin-bottom: -45px; position: relative; z-index: 10;">
            <span class="column-tag">audio_id</span>
            <span class="column-tag">speaker_A_audio</span>
            <span class="column-tag">speaker_B_audio</span>
            <span class="column-tag">combined_audio</span>
            <span class="column-tag">transcription</span>
        </div>
        """, unsafe_allow_html=True)
    
    # The uploader now "contains" the tags above it visually
    main_csv = st.file_uploader("", type=["csv"], label_visibility="collapsed")

# Start Button
_, col_btn = st.columns([4, 1])
with col_btn:
    run_pressed = st.button("Start Validation", disabled=not main_csv)

# --- RESULTS LOGIC ---
if main_csv is not None and run_pressed:
    st.write("---")
    st.success("Validation Started!")
    # ... (rest of your logic for metrics and reports)