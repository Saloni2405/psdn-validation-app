import streamlit as st
import pandas as pd
import time
import json
import os
from io import BytesIO

st.set_page_config(layout="wide", page_title="AudioQA Dataset Validation")

# --- 1. CONSOLIDATED CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Centered Upload Box */
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

    /* Hide default file info */
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderFileData"] { display: none; }

    /* Pill Labels */
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

    /* Pipeline & Status Cards */
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

    /* Headers */
    .preview-header { display: flex; align-items: center; gap: 10px; margin-top: 30px; }
    .status-icon { color: #4CAF50; font-size: 1.2rem; }
    .row-info { color: #808495; font-size: 0.85rem; margin-left: 32px; margin-bottom: 15px; }

    /* Royal Blue Buttons */
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

# --- 2. SESSION INITIALIZATION ---
if 'step' not in st.session_state:
    st.session_state.step = 'upload'
if 'df' not in st.session_state:
    st.session_state.df = None
if 'results' not in st.session_state:
    st.session_state.results = []
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']

# --- 3. CORE QC LOGIC (From Colab) ---
def run_structural_qc_logic(row):
    """Simplified version of your Colab logic for the running loop."""
    try:
        # Check for missing values in CSV
        for col in REQUIRED_COLUMNS:
            if pd.isna(row[col]):
                return "Fail", f"{col.replace('_', ' ').title()}: Missing data"
        
        # Simulate File Check/404 error matching your screenshot
        # In production, replace this with your JSON schema/Librosa checks
        return "Fail", "Speaker A audio: File not found (HTTP 404)"
    except Exception as e:
        return "Fail", str(e)

# --- 4. APP FLOW ---

st.title("NEW VALIDATION RUN")

# --- STEP 1: UPLOAD ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    st.caption("Select folder containing a CSV with Google Drive links and transcription JSONs.")

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
                        <span style="color: #808495; font-size: 0.85rem;">👁️ Showing first 2 rows</span>
                    </div>
                    <div class="row-info">{len(df)} rows parsed</div>
                """, unsafe_allow_html=True)
                st.table(df.head(2))

                col1, col2 = st.columns([5,1])
                with col2:
                    if st.button("Continue →"):
                        st.session_state.step = 'ready'
                        st.rerun()
            else:
                st.error("Missing required columns in CSV.")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# --- STEP 2: READY ---
elif st.session_state.step == 'ready':
    st.write("### Ready to Validate")
    st.write(f"**{len(st.session_state.df)}** rows loaded from `{st.session_state.file_name}`.")

    with st.expander("⚙️ Validation Settings", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.number_input("MIN DURATION (S)", value=1)
        c2.number_input("MAX DURATION (S)", value=600)
        c3.number_input("WER THRESHOLD", value=0.15)
        c4.number_input("CONCURRENCY", value=3)

    st.markdown(f"""
        <div class="pipeline-box">
            <b style="color: #4169E1;">Pipeline configuration:</b><br>
            <span style="font-size: 0.9rem; color: #E0E0E0;">1. Structural check on all {len(st.session_state.df)} rows</span><br>
            <span style="font-size: 0.9rem; color: #E0E0E0;">2. Accuracy check on passing rows only</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("Start Validation"):
            st.session_state.step = 'running'
            st.rerun()
    with col2:
        if st.button("← Back"):
            st.session_state.step = 'upload'
            st.rerun()

# --- STEP 3: RUNNING ---
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
        time.sleep(0.3) 

    st.session_state.results = live_results
    st.session_state.step = 'report'
    st.rerun()

# --- STEP 4: REPORT & DOWNLOAD ---
elif st.session_state.step == 'report':
    res_df = pd.DataFrame(st.session_state.results)
    
    col_a, col_b = st.columns([5, 1])
    with col_b:
        if st.button("New Run"):
            st.session_state.step = 'upload'
            st.session_state.results = []
            st.rerun()

    st.write("### Validation Report")
    st.caption(f"Results for {st.session_state.file_name}")

    # Metrics
    total = len(res_df)
    passed = sum(1 for r in st.session_state.results if "✅ Pass" in r["STRUCTURAL"])
    pass_rate = (passed / total) * 100 if total > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", total)
    m2.metric("Structural Pass", f"{pass_rate:.1f}%", f"{pass_rate - 100:.1f}%")
    m3.metric("Accuracy Pass", "0%")
    m4.metric("Avg WER", "—")

    st.write("#### Detailed Results")
    st.table(res_df)

    # --- DOWNLOAD SECTION ---
    st.markdown("---")
    st.write("### Export Data")
    d_col1, d_col2 = st.columns(2)
    
    # 1. Download CSV Results
    csv_data = res_df.to_csv(index=False).encode('utf-8')
    d_col1.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name=f"validation_report_{st.session_state.file_name}",
        mime="text/csv"
    )

    # 2. Download Detailed Report (Simulated as a Text Summary)
    report_text = f"VALIDATION SUMMARY\nFile: {st.session_state.file_name}\nTotal Rows: {total}\nPass Rate: {pass_rate}%\n\nDetailed Results:\n"
    report_text += res_df.to_string()
    
    d_col2.download_button(
        label="📄 Download Full Report (.txt)",
        data=report_text,
        file_name=f"summary_{st.session_state.file_name}.txt",
        mime="text/plain"
    )