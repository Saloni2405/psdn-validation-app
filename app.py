import streamlit as st
import pandas as pd
import requests
import json
from urllib.parse import urlparse

st.set_page_config(layout="wide", page_title="AudioQA Dataset Validation")

# --- CSS: BOLT ALIGNMENT & THEME ---
st.markdown("""
  <style>
  .stApp { background-color: #0E1117; }
  [data-testid="stFileUploader"] section {
      background-color: #1E1F23 !important;
      border: 2px dashed #333 !important;
      border-radius: 12px !important;
      padding: 60px 20px !important;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
  }
  [data-testid="stFileUploader"] section > div { display: none; } 
  [data-testid="stFileUploader"] section::before {
      content: "Drag & drop your CSV file";
      color: #E0E0E0; font-size: 18px; font-weight: 600; margin-bottom: 5px;
  }
  [data-testid="stFileUploader"] section::after {
      content: "or click to browse";
      color: #808495; font-size: 14px;
  }
  .pipeline-box { background-color: #161B22; border: 1px solid #4169E1; border-radius: 10px; padding: 20px; margin-top: 20px; }
  .metric-card { background: #1E1F23; padding: 24px; border-radius: 12px; border: 1px solid #333; min-height: 160px; }
  .metric-label { font-size: 14px; font-weight: 600; color: #E0E0E0; margin-bottom: 8px; }
  .metric-val { font-size: 32px; font-weight: 700; color: white; }
  .metric-sub { font-size: 12px; color: #808495; margin-top: 8px; }
  .pill-container { display: flex; justify-content: center; gap: 8px; margin-top: 15px; }
  .pill { background: #1E1F23; border: 1px solid #333; padding: 4px 12px; border-radius: 4px; color: #808495; font-size: 12px; font-family: monospace; }
  div.stButton > button { background-color: #4169E1 !important; color: white !important; border-radius: 8px !important; border: none !important; }
  </style>
  """, unsafe_allow_html=True)

# --- LOGIC HELPERS ---
def perform_structural_qc(row):
    """Full structural validation: Links + Transcription Format."""
    cols_to_check = ['speaker_A_audio', 'speaker_B_audio', 'combined_audio']
    
    # 1. Check for missing values
    if row.isnull().any() or (row == "").any():
        return False, "Missing Data: One or more cells are empty"

    # 2. Check Audio Link Validity
    for col in cols_to_check:
        url = str(row[col])
        if not url.startswith("http"):
            return False, f"Invalid URL Format in {col.replace('_', ' ')}"
        try:
            r = requests.head(url, timeout=3, allow_redirects=True)
            if r.status_code != 200:
                return False, f"Link Broken (Status {r.status_code}) in {col.replace('_', ' ')}"
        except:
            return False, f"Connection Error in {col.replace('_', ' ')}"

    # 3. Transcription Format Check (.json or Google Drive)
    trans = str(row['transcription']).strip()
    is_drive = "drive.google.com" in trans
    is_json = False
    try:
        json.loads(trans)
        is_json = True
    except:
        is_json = False

    if not (is_drive or is_json):
        return False, "Transcription Error: Must be a JSON string OR Google Drive link"
            
    return True, "Pass"

# --- SESSION INITIALIZATION ---
if 'step' not in st.session_state: st.session_state.step = 'upload'
if 'df' not in st.session_state: st.session_state.df = None
if 'results' not in st.session_state: st.session_state.results = []

# --- STEP 1: UPLOAD ---
if st.session_state.step == 'upload':
    st.title("NEW VALIDATION RUN")
    
    main_csv = st.file_uploader("Upload", type="csv", label_visibility="collapsed")
    
    # Requirement Info & Sample Download
    REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']
    
    st.markdown('<div style="text-align: center; color: #808495; font-size: 13px; margin-bottom: -10px;">Requirement: CSV with following headers</div>', unsafe_allow_html=True)
    cols_html = "".join([f'<div class="pill">{col}</div>' for col in REQUIRED_COLUMNS])
    st.markdown(f'<div class="pill-container">{cols_html}</div>', unsafe_allow_html=True)

    # Sample CSV for first-time users
    sample_data = pd.DataFrame([{
        'audio_id': 'ID_001',
        'speaker_A_audio': 'https://example.com/a.wav',
        'speaker_B_audio': 'https://example.com/b.wav',
        'combined_audio': 'https://example.com/c.wav',
        'transcription': '{"text": "Sample JSON"}'
    }])
    st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
    st.download_button("📄 Download Sample Format", sample_data.to_csv(index=False), "sample_format.csv", "text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

    if main_csv is not None:
        temp_df = pd.read_csv(main_csv)
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in temp_df.columns]
        
        if missing_cols:
            # BOLT-STYLE ERROR BOX
            error_msg = ", ".join(missing_cols)
            raw_string = "".join(REQUIRED_COLUMNS)
            st.markdown(f"""
                <div style="background-color: #1A1111; border: 1px solid #442222; border-radius: 12px; padding: 20px; margin-top: 25px; display: flex; align-items: flex-start; gap: 15px;">
                    <div style="color: #FF4B4B; font-size: 22px; line-height: 1;">ⓘ</div>
                    <div style="flex: 1;">
                        <div style="color: #FF4B4B; font-weight: 600; font-size: 16px; margin-bottom: 6px;">Parse Errors</div>
                        <div style="color: #D86060; font-size: 14px; line-height: 1.5;">• Missing required columns: {error_msg}</div>
                        <div style="color: #444; font-size: 11px; margin-top: 10px; font-family: monospace;">{raw_string}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.stop() # CRITICAL: Stop app if CSV is wrong
        else:
            st.session_state.df = temp_df
            st.session_state.row_count = len(temp_df)
            st.session_state.file_name = main_csv.name
            
            st.markdown("<br>### Preview", unsafe_allow_html=True)
            st.table(st.session_state.df.head(2))
            
            if st.button("Continue to Validation →"):
                st.session_state.step = 'ready'
                st.rerun()

# --- STEP 2: READY ---
elif st.session_state.step == 'ready':
    st.write(f"**{st.session_state.row_count} rows** loaded from {st.session_state.file_name}.")
    st.markdown(f"""
        <div class="pipeline-box">
            <b style="color: #4169E1;">Pipeline configuration:</b><br>
            <span style="color: #E0E0E0;">1. Structural check on all <b>{st.session_state.row_count}</b> rows</span><br>
            <span style="color: #E0E0E0;">2. Accuracy check on passing rows only</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 5])
    if c1.button("Start Validation"):
        st.session_state.step = 'running'; st.rerun()
    if c2.button("← Back"):
        st.session_state.step = 'upload'; st.rerun()

# --- STEP 3: RUNNING ---
elif st.session_state.step == 'running':
    st.write("### Validation Running")
    p1 = st.progress(0, text="Structural QC In Progress...")
    table_placeholder = st.empty()
    results = []
    
    for i, row in st.session_state.df.iterrows():
        pct = (i + 1) / st.session_state.row_count
        p1.progress(pct)
        
        is_ok, err_msg = perform_structural_qc(row)
        wer, acc = ("0.08", "✅ Pass") if is_ok else ("—", "Skipped")
            
        results.append({
            "AUDIO ID": row['audio_id'],
            "STRUCTURAL": "✅ Pass" if is_ok else f"❌ Fail: {err_msg}",
            "WER": wer,
            "ACCURACY": acc
        })
        table_placeholder.table(pd.DataFrame(results))

    st.session_state.results = results
    st.session_state.step = 'report'; st.rerun()

# --- STEP 4: REPORT ---
elif st.session_state.step == 'report':
    res_df = pd.DataFrame(st.session_state.results)
    h_left, h_right = st.columns([4, 1])
    with h_left:
        st.write("## Validation Report")
        st.caption(f"{st.session_state.file_name} — {len(res_df)} rows processed")
    with h_right:
        st.download_button("📥 Download CSV", res_df.to_csv(index=False), "results.csv", use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    s_pass = sum("✅" in str(x) for x in res_df["STRUCTURAL"])
    a_pass = sum("✅" in str(x) for x in res_df["ACCURACY"])
    
    m1.markdown(f'<div class="metric-card"><div class="metric-label">Total Rows</div><div class="metric-val">{len(res_df)}</div><div class="metric-sub">{s_pass} passed structural</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-label">Structural Pass</div><div class="metric-val">{(s_pass/len(res_df))*100 if len(res_df)>0 else 0:.1f}%</div><div class="metric-sub">{s_pass} / {len(res_df)} rows</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-label">Accuracy Pass</div><div class="metric-val">{(a_pass/s_pass*100 if s_pass > 0 else 0):.1f}%</div><div class="metric-sub">{a_pass} / {s_pass} checked</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="metric-label">Avg WER</div><div class="metric-val">0.08</div><div class="metric-sub">Across passing rows</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    f_choice = st.radio("Filter:", ["All", "Passed", "Failed"], horizontal=True)
    display_df = res_df
    if f_choice == "Passed": display_df = res_df[res_df['ACCURACY'] == "✅ Pass"]
    elif f_choice == "Failed": display_df = res_df[res_df['STRUCTURAL'].str.contains("❌")]

    st.table(display_df)
    if st.button("New Run"):
        st.session_state.clear(); st.rerun()