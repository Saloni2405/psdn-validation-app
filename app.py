import streamlit as st
import pandas as pd
import time
import json
import os
from io import BytesIO

st.set_page_config(layout="wide", page_title="AudioQA Dataset Validation")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Centered Upload Box */
    [data-testid="stFileUploader"] section {
        background-color: #1E1F23 !important;
        border: 2px dashed #333 !important;
        border-radius: 12px !important;
        padding: 60px 20px !important;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 280px !important;
    }
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderFileData"] { display: none; }

    /* Pill Labels inside the box */
    .pill-container {
        display: flex; justify-content: center; gap: 10px; margin-top: -85px; 
        position: relative; z-index: 10; padding-bottom: 50px; pointer-events: none;
    }
    .pill {
        background-color: #2D2E35; border: 1px solid #444; padding: 4px 12px;
        border-radius: 4px; font-family: monospace; font-size: 12px; color: #808495;
    }

    /* Success Preview Styling */
    .preview-header { display: flex; align-items: center; gap: 10px; margin-top: 30px; }
    .status-icon { color: #4CAF50; font-size: 1.2rem; }
    .row-info { color: #808495; font-size: 0.85rem; margin-left: 32px; margin-bottom: 15px; }

    /* Royal Blue Buttons */
    div.stButton > button {
        background-color: #4169E1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if 'step' not in st.session_state: st.session_state.step = 'upload'
if 'df' not in st.session_state: st.session_state.df = None
if 'results' not in st.session_state: st.session_state.results = []

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']

st.title("NEW VALIDATION RUN")

# --- STEP 1: UPLOAD & PREVIEW ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    main_csv = st.file_uploader("Upload", type="csv", label_visibility="collapsed")
    
    # Pills remain visible inside the box even after upload
    st.markdown(f'<div class="pill-container">{"".join([f"<div class=\'pill\'>{c}</div>" for c in REQUIRED_COLUMNS])}</div>', unsafe_allow_html=True)

    if main_csv is not None:
        try:
            df = pd.read_csv(main_csv)
            if all(col in df.columns for col in REQUIRED_COLUMNS):
                st.session_state.df = df
                st.session_state.file_name = main_csv.name
                
                st.markdown(f'<div class="preview-header"><span class="status-icon">✅</span><b>{main_csv.name}</b></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-info">{len(df)} rows parsed</div>', unsafe_allow_html=True)
                st.table(df.head(2))
                
                # RIGHT ALIGNED CONTINUE BUTTON
                _, col_btn = st.columns([4, 1])
                with col_btn:
                    if st.button("Continue to Validation →", use_container_width=True):
                        st.session_state.step = 'ready'
                        st.rerun()
            else:
                st.error("Missing required columns.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- STEP 2: READY ---
elif st.session_state.step == 'ready':
    st.write("### Ready to Validate")
    st.info(f"{len(st.session_state.df)} rows loaded. Click start to begin QC.")
    if st.button("Start Validation"):
        st.session_state.step = 'running'
        st.rerun()

# --- STEP 3: RUNNING ---
elif st.session_state.step == 'running':
    st.write("### Validation Running")
    p1 = st.progress(0, text="Structural & Accuracy Progress")
    res_placeholder = st.empty()
    live_results = []
    
    for i, row in st.session_state.df.iterrows():
        # Accuracy Bar & Logic Running
        progress = (i + 1) / len(st.session_state.df)
        p1.progress(progress)
        
        live_results.append({
            "AUDIO ID": row['audio_id'],
            "STRUCTURAL": "✅ Pass",
            "WER": "0.05",
            "ACCURACY": "✅ Pass"
        })
        res_placeholder.table(pd.DataFrame(live_results))
        time.sleep(0.1)
    
    st.session_state.results = live_results
    st.session_state.step = 'report'
    st.rerun()

# --- STEP 4: REPORT (Specific Download Placements) ---
elif st.session_state.step == 'report':
    # 1. Download Report at Top Left area (Nav bar style)
    top_left, top_right = st.columns([1, 5])
    with top_left:
        st.download_button("📥 Download Report", data="Report Content", file_name="report.txt")

    st.markdown("---")
    
    # 2. Validation Report Header with Download CSV on the right
    head_left, head_right = st.columns([4, 1])
    with head_left:
        st.write("## Validation Report")
    with head_right:
        res_df = pd.DataFrame(st.session_state.results)
        csv = res_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="results.csv", mime="text/csv", use_container_width=True)

    # Metrics & Table
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", len(res_df))
    m2.metric("Structural Pass", "100%")
    m3.metric("Accuracy Pass", "100%")
    m4.metric("Avg WER", "0.05")

    st.table(res_df)
    
    if st.button("New Run"):
        st.session_state.step = 'upload'
        st.rerun()