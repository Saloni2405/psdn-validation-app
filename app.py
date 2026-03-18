import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide")

# Final CSS containing all styles for Upload, Running, and Report states
st.markdown("""
   <style>
   .stApp { background-color: #0E1117; }
  
   /* 1. Large, Centered Upload Box */
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

   [data-testid="stFileUploader"] button {
       background-color: #2D2E35 !important;
       border: 1px solid #444 !important;
       color: white !important;
       border-radius: 8px !important;
   }

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

   /* 2. Success Preview & Pipeline Card Styling */
   .preview-header { display: flex; align-items: center; gap: 10px; margin-top: 30px; }
   .status-icon { color: #4CAF50; font-size: 1.2rem; }
   .row-info { color: #808495; font-size: 0.85rem; margin-left: 32px; margin-bottom: 15px; }
   .showing-text { color: #808495; font-size: 0.85rem; float: right; }

   /* Pipeline Blue Box */
   .pipeline-box {
       background-color: #161B22;
       border: 1px solid #4169E1;
       border-radius: 10px;
       padding: 20px;
       margin-top: 20px;
       display: flex;
       justify-content: space-between;
       align-items: center;
   }

   /* 3. Royal Blue Buttons */
   div.stButton > button {
       background-color: #4169E1 !important;
       color: white !important;
       border: none !important;
       padding: 10px 24px !important;
       border-radius: 8px !important;
       font-weight: 500 !important;
   }

   /* 4. Running & Report Specific Styles */
   .status-card {
       background-color: #1E1F23;
       border: 1px solid #333;
       border-radius: 10px;
       padding: 20px;
       margin-bottom: 10px;
   }
   </style>
   """, unsafe_allow_html=True)

# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 'upload'

st.title("NEW VALIDATION RUN")

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']

# --- STEP 1: UPLOAD & PREVIEW ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    st.caption("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

    with st.container():
        main_csv = st.file_uploader("Drag & drop your CSV file here", type="csv", label_visibility="collapsed")
        st.markdown(f'<div class="pill-container">{"".join([f"<div class=\'pill\'>{c}</div>" for c in REQUIRED_COLUMNS])}</div>', unsafe_allow_html=True)

    if main_csv is not None:
        try:
            df = pd.read_csv(main_csv)
            if not any(col not in df.columns for col in REQUIRED_COLUMNS):
                st.markdown(f"""
                    <div class="preview-header">
                        <span class="status-icon">✅</span>
                        <span style="font-weight: 500; color: #E0E0E0;">{main_csv.name}</span>
                        <span style="flex-grow: 1;"></span>
                        <span class="showing-text">👁️ Showing first 2 rows</span>
                    </div>
                    <div class="row-info">{len(df)} rows parsed</div>
                """, unsafe_allow_html=True)
                
                st.table(df.head(2))

                col1, col2 = st.columns([5,1])
                with col2:
                    if st.button("Continue to Validation →"):
                        st.session_state.step = 'ready'
                        st.session_state.row_count = len(df)
                        st.session_state.file_name = main_csv.name
                        st.rerun()
            else:
                st.error("Missing required columns.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- STEP 2: READY TO VALIDATE ---
elif st.session_state.step == 'ready':
    st.write("### Ready to Validate")
    st.write(f"{st.session_state.row_count} rows loaded from **{st.session_state.file_name}**. Click below to start the validation pipeline.")

    with st.expander("⚙️ Validation Settings", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.number_input("MIN DURATION (S)", value=1)
        c2.number_input("MAX DURATION (S)", value=600)
        c3.number_input("WER THRESHOLD", value=0.15)
        c4.number_input("CONCURRENCY", value=3)

    st.markdown(f"""
        <div class="pipeline-box">
            <div>
                <b style="color: #4169E1;">Pipeline will run:</b><br>
                <span style="font-size: 0.9rem; color: #E0E0E0;">1. Structural check on all {st.session_state.row_count} rows</span><br>
                <span style="font-size: 0.9rem; color: #E0E0E0;">2. Accuracy check on passing rows only</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Start Validation"):
        st.session_state.step = 'running'
        st.rerun()

    if st.button("← Back to Upload"):
        st.session_state.step = 'upload'
        st.rerun()

# --- STEP 3: VALIDATION RUNNING ---
elif st.session_state.step == 'running':
    st.write("### Validation Running")
    st.caption(f"Processing {st.session_state.row_count} rows...")

    # Stepper UI
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown("✅ **Upload**")
    s2.markdown("🔵 **Structural Check**")
    s3.markdown("⚪ Accuracy Check")
    s4.markdown("⚪ Report")

    # Progress Cards
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="status-card"><b>Structural Check</b><br><small>Processing {st.session_state.row_count} rows...</small></div>', unsafe_allow_html=True)
        st.progress(50)
    with c2:
        st.markdown('<div class="status-card" style="opacity:0.5;"><b>Accuracy Check</b><br><small>Waiting for structural...</small></div>', unsafe_allow_html=True)
        st.progress(0)

    st.write("#### Live Results")
    # Simulated Live Table
    live_df = pd.DataFrame([
        {"AUDIO ID": "test_001", "STRUCTURAL": "Processing...", "WER": "—", "ACCURACY": "Processing..."},
        {"AUDIO ID": "test_002", "STRUCTURAL": "Processing...", "WER": "—", "ACCURACY": "Processing..."}
    ])
    st.table(live_df)
    
    if st.button("Finish & View Report"):
        st.session_state.step = 'report'
        st.rerun()

# --- STEP 4: VALIDATION REPORT ---
elif st.session_state.step == 'report':
    t1, t2 = st.columns([5, 1])
    with t2:
        if st.button("New Run"):
            st.session_state.step = 'upload'
            st.rerun()

    st.write("### Validation Report")
    st.caption(f"{st.session_state.file_name} — {st.session_state.row_count} rows processed")

    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", st.session_state.row_count)
    m2.metric("Structural Pass", "0.0%", "-100%")
    m3.metric("Accuracy Pass", "N/A")
    m4.metric("Avg WER", "N/A")

    # Error Table
    st.write("#### Detailed Results")
    results_df = pd.DataFrame([
        {"AUDIO ID": "test_001", "STRUCTURAL": "❌ Fail: File not found (404)", "WER SCORE": "—", "ACCURACY": "Skipped"},
        {"AUDIO ID": "test_002", "STRUCTURAL": "❌ Fail: File not found (404)", "WER SCORE": "—", "ACCURACY": "Skipped"}
    ])
    st.table(results_df)
    st.download_button("Download CSV Report", data="audio_id,status\ntest_001,fail\ntest_002,fail", file_name="report.csv")