import streamlit as st
import pandas as pd
import time
import json
import os

st.set_page_config(layout="wide")

# --- CSS STYLES ---
st.markdown("""
   <style>
   .stApp { background-color: #0E1117; }
   [data-testid="stFileUploader"] section {
       background-color: #1E1F23 !important;
       border: 2px dashed #333 !important;
       border-radius: 12px !important;
       padding: 60px 20px !important;
       display: flex;
       flex-direction: column; align-items: center; justify-content: center;
       min-height: 280px !important;
   }
   [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderFileData"] { display: none; }
   [data-testid="stFileUploader"] button {
       background-color: #2D2E35 !important; border: 1px solid #444 !important;
       color: white !important; border-radius: 8px !important;
   }
   .pill-container {
       display: flex; justify-content: center; gap: 10px; margin-top: -85px; 
       position: relative; z-index: 10; padding-bottom: 50px;
   }
   .pill {
       background-color: #2D2E35; border: 1px solid #444; padding: 4px 12px;
       border-radius: 4px; font-family: monospace; font-size: 12px; color: #808495;
   }
   .preview-header { display: flex; align-items: center; gap: 10px; margin-top: 30px; }
   .status-icon { color: #4CAF50; font-size: 1.2rem; }
   .row-info { color: #808495; font-size: 0.85rem; margin-left: 32px; margin-bottom: 15px; }
   .showing-text { color: #808495; font-size: 0.85rem; float: right; }
   .pipeline-box {
       background-color: #161B22; border: 1px solid #4169E1; border-radius: 10px;
       padding: 20px; margin-top: 20px;
   }
   div.stButton > button {
       background-color: #4169E1 !important; color: white !important;
       border: none !important; padding: 10px 24px !important;
       border-radius: 8px !important; font-weight: 500 !important;
   }
   .status-card {
       background-color: #1E1F23; border: 1px solid #333;
       border-radius: 10px; padding: 20px; margin-bottom: 10px;
   }
   </style>
   """, unsafe_allow_html=True)

# --- CORE QC LOGIC (From your Colab) ---
def to_seconds(ts):
    if not ts: return 0
    try:
        parts = list(map(float, str(ts).strip().split(':')))
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2: return parts[0] * 60 + parts[1]
        return float(parts[0])
    except: return 0

def run_structural_qc_logic(row):
    """Integrates your Colab logic for a single row of the CSV"""
    # This is a simplified version of your function for the Streamlit loop
    try:
        # Check if the transcription is a valid JSON string or path
        transcription_raw = row['transcription']
        
        # Simulation of file checking (Since real paths vary between Colab/Local)
        if pd.isna(transcription_raw):
            return "Reject", "Missing transcription column data"
        
        # Logic: If path doesn't exist locally, we return the error you saw in your screenshot
        if not os.path.exists(str(transcription_raw)):
            return "Reject", f"File not found: {transcription_raw}"

        return "Accept", "Passed structural check"
    except Exception as e:
        return "Reject", str(e)

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 'upload'
if 'df' not in st.session_state:
    st.session_state.df = None
if 'results' not in st.session_state:
    st.session_state.results = []

st.title("NEW VALIDATION RUN")
REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']

# --- STEP 1: UPLOAD ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    with st.container():
        main_csv = st.file_uploader("Upload", type="csv", label_visibility="collapsed")
        st.markdown(f'<div class="pill-container">{"".join([f"<div class=\'pill\'>{c}</div>" for c in REQUIRED_COLUMNS])}</div>', unsafe_allow_html=True)

    if main_csv is not None:
        df = pd.read_csv(main_csv)
        st.session_state.df = df
        st.markdown(f'<div class="preview-header"><span class="status-icon">✅</span><b>{main_csv.name}</b></div>', unsafe_allow_html=True)
        st.table(df.head(2))
        
        col1, col2 = st.columns([5,1])
        with col2:
            if st.button("Continue to Validation →"):
                st.session_state.step = 'ready'
                st.session_state.file_name = main_csv.name
                st.rerun()

# --- STEP 2: READY ---
elif st.session_state.step == 'ready':
    st.write("### Ready to Validate")
    with st.expander("⚙️ Validation Settings", expanded=False):
        st.columns(4)[0].number_input("MIN DURATION (S)", value=1)
    
    st.markdown(f'<div class="pipeline-box"><b style="color:#4169E1;">Pipeline will run:</b><br>1. Structural check on {len(st.session_state.df)} rows</div>', unsafe_allow_html=True)
    
    if st.button("Start Validation"):
        st.session_state.step = 'running'
        st.rerun()

# --- STEP 3: RUNNING (Automated Processing) ---
elif st.session_state.step == 'running':
    st.write("### Validation Running")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="status-card"><b>Structural Check</b></div>', unsafe_allow_html=True)
        p1 = st.progress(0)
    with c2:
        st.markdown('<div class="status-card" style="opacity:0.5;"><b>Accuracy Check</b></div>', unsafe_allow_html=True)
        p2 = st.progress(0)

    results_placeholder = st.empty()
    live_results = []
    
    # Process rows automatically
    for i, row in st.session_state.df.iterrows():
        decision, detail = run_structural_qc_logic(row)
        
        live_results.append({
            "AUDIO ID": row['audio_id'],
            "STRUCTURAL": "✅ Pass" if decision == "Accept" else f"❌ {detail}",
            "WER": "—",
            "ACCURACY": "Skipped" if decision == "Reject" else "Processing..."
        })
        
        # Update progress and table
        p1.progress((i + 1) / len(st.session_state.df))
        results_placeholder.table(pd.DataFrame(live_results))
        time.sleep(0.5) # Simulated processing time

    st.session_state.results = live_results
    st.session_state.step = 'report'
    st.rerun()

# --- STEP 4: REPORT ---
elif st.session_state.step == 'report':
    t1, t2 = st.columns([5, 1])
    with t2:
        if st.button("New Run"):
            st.session_state.step = 'upload'
            st.session_state.results = []
            st.rerun()

    st.write("### Validation Report")
    
    # Calculate real pass rate
    pass_count = sum(1 for r in st.session_state.results if "✅ Pass" in r["STRUCTURAL"])
    total = len(st.session_state.results)
    pass_rate = (pass_count / total) * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", total)
    m2.metric("Structural Pass", f"{pass_rate}%", f"{pass_rate - 100}%")
    m3.metric("Accuracy Pass", "0%")
    m4.metric("Avg WER", "—")

    st.write("#### Detailed Results")
    st.table(pd.DataFrame(st.session_state.results))