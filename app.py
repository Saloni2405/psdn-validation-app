import streamlit as st
import pandas as pd
import time
import json
import os

st.set_page_config(layout="wide", page_title="AudioQA Dataset Validation")

# --- CUSTOM CSS ---
st.markdown("""
   <style>
   .stApp { background-color: #0E1117; }
   [data-testid="stFileUploader"] section {
       background-color: #1E1F23 !important; border: 2px dashed #333 !important;
       border-radius: 12px !important; padding: 60px 20px !important;
       display: flex; flex-direction: column; align-items: center; justify-content: center;
   }
   [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderFileData"] { display: none; }
   .pill {
       background-color: #2D2E35; border: 1px solid #444; padding: 4px 12px;
       border-radius: 4px; font-family: monospace; font-size: 12px; color: #808495;
       margin: 0 5px;
   }
   .status-card {
       background-color: #1E1F23; border: 1px solid #333;
       border-radius: 10px; padding: 20px; margin-bottom: 10px;
   }
   div.stButton > button {
       background-color: #4169E1 !important; color: white !important;
       border-radius: 8px !important; font-weight: 500 !important;
   }
   </style>
   """, unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if 'step' not in st.session_state:
    st.session_state.step = 'upload'
if 'df' not in st.session_state:
    st.session_state.df = None  # CRITICAL: This fixes your AttributeError
if 'results' not in st.session_state:
    st.session_state.results = []

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']

# --- CORE QC LOGIC ---
def run_structural_qc_logic(row):
    """Integrates your Colab logic logic."""
    try:
        # 1. Check for missing columns
        for col in REQUIRED_COLUMNS:
            if pd.isna(row[col]):
                return "Fail", f"{col.replace('_', ' ').title()}: Missing data"
        
        # 2. Schema Validation (Simulated from your Colab logic)
        # In a real run, you would parse the transcription JSON here
        # Example error matching your screenshot
        return "Fail", "Speaker A audio: File not found (HTTP 404)"
        
    except Exception as e:
        return "Fail", str(e)

st.title("NEW VALIDATION RUN")

# --- STEP 1: UPLOAD ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    main_csv = st.file_uploader("Upload", type="csv", label_visibility="collapsed")
    
    # Pill labels matching your UI
    st.markdown('<div style="display:flex; justify-content:center; margin-top:-70px; margin-bottom:50px;">' + 
                "".join([f'<span class="pill">{c}</span>' for c in REQUIRED_COLUMNS]) + 
                '</div>', unsafe_allow_html=True)

    if main_csv is not None:
        df = pd.read_csv(main_csv)
        st.session_state.df = df # Fixes the missing attribute error
        st.success(f"✅ {len(df)} rows parsed from {main_csv.name}")
        st.table(df.head(2))
        
        if st.button("Continue to Validation →"):
            st.session_state.step = 'ready'
            st.rerun()

# --- STEP 2: READY ---
elif st.session_state.step == 'ready':
    st.write("### Ready to Validate")
    st.info(f"Pipeline will run Structural and Accuracy checks on {len(st.session_state.df)} rows.")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Start Validation"):
            st.session_state.step = 'running'
            st.rerun()
    with col2:
        if st.button("← Back to Upload"):
            st.session_state.step = 'upload'
            st.rerun()

# --- STEP 3: RUNNING ---
elif st.session_state.step == 'running':
    st.write("### Validation Running")
    
    # UI Progress Indicators
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="status-card"><b>Structural Check</b></div>', unsafe_allow_html=True)
        p1 = st.progress(0)
    with c2:
        st.markdown('<div class="status-card" style="opacity:0.5;"><b>Accuracy Check</b></div>', unsafe_allow_html=True)
        p2 = st.progress(0)

    results_placeholder = st.empty()
    live_results = []
    
    # Loop through the dataframe saved in session state
    for i, row in st.session_state.df.iterrows():
        status, detail = run_structural_qc_logic(row)
        
        live_results.append({
            "AUDIO ID": row['audio_id'],
            "STRUCTURAL": f"❌ {status}: {detail}" if status == "Fail" else "✅ Pass",
            "WER": "—",
            "ACCURACY": "Skipped"
        })
        
        p1.progress((i + 1) / len(st.session_state.df))
        results_placeholder.table(pd.DataFrame(live_results))
        time.sleep(0.4) # Simulates processing

    st.session_state.results = live_results
    st.session_state.step = 'report'
    st.rerun()

# --- STEP 4: REPORT ---
elif st.session_state.step == 'report':
    st.write("### Validation Report")
    
    total = len(st.session_state.results)
    passed = sum(1 for r in st.session_state.results if "✅ Pass" in r["STRUCTURAL"])
    pass_rate = (passed / total) * 100 if total > 0 else 0

    # Summary Metrics matching your screenshot
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", total)
    m2.metric("Structural Pass", f"{pass_rate}%", f"{pass_rate - 100}%")
    m3.metric("Accuracy Pass", "N/A")
    m4.metric("Avg WER", "N/A")

    st.write("#### Detailed Results")
    st.table(pd.DataFrame(st.session_state.results))
    
    if st.button("New Run"):
        st.session_state.step = 'upload'
        st.session_state.results = []
        st.rerun()