import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide", page_title="AudioQA Dataset Validation")

# --- CONSOLIDATED CSS ---
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
      pointer-events: none;
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

  /* Running State Status Cards */
  .status-card {
      background-color: #1E1F23;
      border: 1px solid #333;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 10px;
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
  </style>
  """, unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if 'step' not in st.session_state:
    st.session_state.step = 'upload'
if 'df' not in st.session_state:
    st.session_state.df = None
if 'results' not in st.session_state:
    st.session_state.results = []

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']

st.title("NEW VALIDATION RUN")

# --- STEP 1: UPLOAD & PREVIEW ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    st.caption("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

    with st.container():
        main_csv = st.file_uploader("Drag & drop your CSV file here", type="csv", label_visibility="collapsed")
        # Pills kept persistent inside the box
        st.markdown(f'<div class="pill-container">{"".join([f"<div class=\'pill\'>{c}</div>" for c in REQUIRED_COLUMNS])}</div>', unsafe_allow_html=True)

    if main_csv is not None:
        try:
            df = pd.read_csv(main_csv)
            if all(col in df.columns for col in REQUIRED_COLUMNS):
                st.session_state.df = df
                st.session_state.row_count = len(df)
                st.session_state.file_name = main_csv.name
                
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

                # Right Aligned Continue Button
                col_space, col_btn = st.columns([5,1])
                with col_btn:
                    if st.button("Continue to Validation →", use_container_width=True):
                        st.session_state.step = 'ready'
                        st.rerun()
            else:
                st.error("Missing required columns.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- STEP 2: READY TO VALIDATE ---
elif st.session_state.step == 'ready':
    st.write("### Ready to Validate")
    st.write(f"{st.session_state.row_count} rows loaded from **{st.session_state.file_name}**.")

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
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Start Validation"):
            st.session_state.step = 'running'
            st.rerun()
    with col2:
        if st.button("← Back to Upload"):
            st.session_state.step = 'upload'
            st.rerun()

# --- STEP 3: RUNNING (Accuracy Bar Fixed) ---
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
    
    for i, row in st.session_state.df.iterrows():
        # Update both progress bars
        progress_val = (i + 1) / len(st.session_state.df)
        p1.progress(progress_val)
        p2.progress(progress_val)
        
        # Simulating logic
        live_results.append({
            "AUDIO ID": row['audio_id'],
            "STRUCTURAL": "✅ Pass",
            "WER": "0.08",
            "ACCURACY": "✅ Pass"
        })
        results_placeholder.table(pd.DataFrame(live_results))
        time.sleep(0.1)

    st.session_state.results = live_results
    st.session_state.step = 'report'
    st.rerun()

# --- STEP 4: REPORT (Download placements fixed) ---
elif st.session_state.step == 'report':
    # Download Report at Top Left
    t_left, t_right = st.columns([1, 5])
    with t_left:
        st.download_button("📥 Download Report", data="Full Report Data", file_name="report.txt")

    st.markdown("---")
    
    # Validation Report Header with Download CSV on right
    h_left, h_right = st.columns([4, 1])
    with h_left:
        st.write("## Validation Report")
    with h_right:
        res_df = pd.DataFrame(st.session_state.results)
        csv = res_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="results.csv", mime="text/csv", use_container_width=True)

    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", len(res_df))
    m2.metric("Structural Pass", "100%")
    m3.metric("Accuracy Pass", "100%")
    m4.metric("Avg WER", "0.08")

    st.table(res_df)
    
    if st.button("New Run"):
        st.session_state.step = 'upload'
        st.rerun()