import streamlit as st
import pandas as pd

# Set Page Config
st.set_page_config(page_title="AudioQA Pipeline", layout="wide")

# Initialize Session State for navigation
if 'step' not in st.session_state:
    st.session_state.step = 1

# Custom CSS for UI elements
st.markdown("""
    <style>
    /* Royal Blue Button */
    .stButton>button {
        background-color: #2b6cb0;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    /* Parameter Boxes */
    .param-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #dee2e6;
        text-align: center;
        font-weight: 500;
    }
    /* Stepper Styling */
    .stepper-active {
        color: #2b6cb0;
        font-weight: bold;
        border-bottom: 3px solid #2b6cb0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("⚡ AudioQA")
st.caption("Dataset Validation Pipeline")

# --- STEPPER INDICATOR ---
s1, s2, s3, s4 = st.columns(4)
with s1: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 1 else ''}'>✅ Upload</div>", unsafe_allow_html=True)
with s2: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 2 else ''}'>🔍 Structural Check</div>", unsafe_allow_html=True)
with s3: st.write("🎯 Accuracy Check")
with s4: st.write("📊 Report")
st.divider()

# --- PAGE 1: UPLOAD ---
if st.session_state.step == 1:
    st.header("New Validation Run")
    
    with st.container(border=True):
        uploaded_file = st.file_uploader("Drag and drop CSV file here", type=["csv"])
        
        st.write("**Required Parameters:**")
        p_cols = st.columns(5)
        params = ["audio_id", "speaker_A_audio", "speaker_B_audio", "combined_audio", "transcription"]
        for col, p in zip(p_cols, params):
            col.markdown(f"<div class='param-box'>{p}</div>", unsafe_allow_html=True)
        
        # Parse Error Mockup (Visible by default as per your request)
        st.error("""
            **Parse Errors** • Missing required columns: audio_id, speaker_A_audio, speaker_B_audio, combined_audio, transcription
        """)

    if st.button("Continue to validation →"):
        st.session_state.step = 2
        st.rerun()

# --- PAGE 2: READY TO VALIDATE ---
elif st.session_state.step == 2:
    st.subheader("Ready to Validate")
    st.write("2 rows loaded from **Untitled spreadsheet.csv**. Click below to start the validation pipeline.")
    
    with st.container(border=True):
        st.markdown("⚙️ **Validation Settings**")
        v1, v2, v3, v4 = st.columns(4)
        with v1: st.number_input("MIN DURATION (S)", value=1)
        with v2: st.number_input("MAX DURATION (S)", value=600)
        with v3: st.number_input("WER THRESHOLD", value=0.15)
        with v4: st.number_input("CONCURRENCY", value=3)

    st.write("") # Spacer
    
    # Blue Info Box and Start Button
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info("""
            **Pipeline will run:** 1. Structural check on all 2 rows  
            2. Accuracy check on passing rows only
            """)
        with c2:
            st.write("###") # Alignment
            if st.button("⚡ Start Validation"):
                st.success("Pipeline Started!")

    if st.button("← Back to Upload"):
        st.session_state.step = 1
        st.rerun()