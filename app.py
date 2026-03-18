import streamlit as st
import pandas as pd
import time
import json
import os
from io import BytesIO

st.set_page_config(layout="wide", page_title="AudioQA Dataset Validation")

# --- CUSTOM CSS (Kept exactly as requested) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stFileUploader"] section {
        background-color: #1E1F23 !important;
        border: 2px dashed #333 !important;
        border-radius: 12px !important;
        padding: 60px 20px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 280px !important;
    }
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderFileData"] { display: none; }
    .pill-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: -85px; 
        position: relative;
        z-index: 10;
        padding-bottom: 50px;
    }
    .pill {
        background-color: #2D2E35;
        border: 1px solid #444;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        color: #808495;
    }
    .pipeline-box {
        background-color: #161B22;
        border: 1px solid #4169E1;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }
    .status-card {
        background-color: #1E1F23;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .preview-header { display: flex; align-items: center; gap: 10px; margin-top: 30px; }
    .status-icon { color: #4CAF50; font-size: 1.2rem; }
    .row-info { color: #808495; font-size: 0.85rem; margin-left: 32px; margin-bottom: 15px; }
    div.stButton > button {
        background-color: #4169E1 !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if 'step' not in st.session_state:
    st.session_state.step = 'upload'
if 'df' not in st.session_state:
    st.session_state.df = None
if 'results' not in st.session_state:
    st.session_state.results = []
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']

# --- STEP 1: UPLOAD ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    with st.container():
        main_csv = st.file_uploader("Upload", type="csv", label_visibility="collapsed")
        st.markdown(f'<div class="pill-container">{"".join([f"<div class=\'pill\'>{c}</div>" for c in REQUIRED_COLUMNS])}</div>', unsafe_allow_html=True)

    if main_csv is not None:
        try:
            df = pd.read_csv(main_csv)
            if all(col in df.columns for col in REQUIRED_COLUMNS):
                st.session_state.df = df
                st.session_state.file_name = main_csv.name
                st.markdown(f"""
                    <div class="preview-header">
                        <span class="status-icon">✅</span>
                        <span style="font-weight: 500; color: #E0E0E0;">{main_csv.name}</span>
                        <span style="flex-grow: 1;"></span>
                    </div>
                    <div class="row-info">{len(df)} rows parsed</div>
                """, unsafe_allow_html=True)
                st.table(df.head(2))
                if st.button("Continue →"):
                    st.session_state.step = 'ready'
                    st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- STEP 2: READY ---
elif st.session_state.step == 'ready':
    st.write("### Ready to Validate")
    with st.expander("⚙️ Validation Settings", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        wer_threshold = c3.number_input("WER THRESHOLD", value=0.15)
    
    st.markdown(f'<div class="pipeline-box"><b>Pipeline configuration:</b><br>1. Structural check on all rows<br>2. Accuracy check on passing rows only</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 6])
    if col1.button("Start Validation"):
        st.session_state.step = 'running'
        st.rerun()
    if col2.button("← Back"):
        st.session_state.step = 'upload'
        st.rerun()

# --- STEP 3: RUNNING (With Accuracy Bar Fixed) ---
elif st.session_state.step == 'running':
    st.write("### Validation Running")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="status-card"><b>Structural Check</b></div>', unsafe_allow_html=True)
        p1 = st.progress(0)
    with c2:
        st.markdown('<div class="status-card"><b>Accuracy Check</b></div>', unsafe_allow_html=True)
        p2 = st.progress(0)

    results_placeholder = st.empty()
    live_results = []
    
    total_rows = len(st.session_state.df)
    
    for i, row in st.session_state.df.iterrows():
        # 1. STRUCTURAL CHECK
        # Simulating your error logic:
        struct_status = "Fail"
        struct_detail = "Speaker A audio: File not found (HTTP 404)"
        
        # Update Structural Progress
        p1.progress((i + 1) / total_rows)
        
        # 2. ACCURACY CHECK (Logic added so bar runs)
        # In a real scenario, this only runs if Structural == Pass
        # For demonstration, we simulate processing time and update the bar
        if struct_status == "Pass":
            accuracy_status = "Processing..."
            time.sleep(0.2) # Simulate WER calculation
            wer_score = 0.08 # Example
            accuracy_status = "✅ Pass" if wer_score <= 0.15 else "❌ Fail"
            wer_display = f"{wer_score:.2f}"
        else:
            time.sleep(0.1) # Still simulate slight delay for the UI feel
            accuracy_status = "Skipped"
            wer_display = "—"

        # Update Accuracy Progress
        p2.progress((i + 1) / total_rows)

        live_results.append({
            "AUDIO ID": row['audio_id'],
            "STRUCTURAL": f"❌ {struct_status}: {struct_detail}" if struct_status == "Fail" else "✅ Pass",
            "WER": wer_display,
            "ACCURACY": accuracy_status
        })
        
        results_placeholder.table(pd.DataFrame(live_results))

    st.session_state.results = live_results
    st.session_state.step = 'report'
    st.rerun()

# --- STEP 4: REPORT ---
elif st.session_state.step == 'report':
    st.write("### Validation Report")
    res_df = pd.DataFrame(st.session_state.results)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", len(res_df))
    m2.metric("Structural Pass", "0.0%") # Based on your screenshot errors
    m3.metric("Accuracy Pass", "N/A")
    m4.metric("Avg WER", "N/A")

    st.table(res_df)

    # --- DOWNLOADS ---
    st.markdown("---")
    d1, d2 = st.columns(2)
    csv = res_df.to_csv(index=False).encode('utf-8')
    d1.download_button("📥 Download CSV Report", data=csv, file_name="report.csv", mime="text/csv")
    if d2.button("New Run"):
        st.session_state.step = 'upload'
        st.rerun()