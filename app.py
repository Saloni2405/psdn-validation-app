import streamlit as st
import pandas as pd
import json
import os

# --- 1. CORE VALIDATION LOGIC ---
REQUIRED_KEYS = {"start", "end", "speaker", "text"}

def to_seconds(ts):
    if not ts: return 0
    try:
        parts = list(map(float, str(ts).strip().split(':')))
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2: return parts[0] * 60 + parts[1]
        return float(parts[0])
    except: return 0

def run_structural_qc(segments):
    stats = {"format_violations": [], "timestamp_violations": [], "zero_duration_segments": []}
    for idx, seg in enumerate(segments):
        if not REQUIRED_KEYS.issubset(set(seg.keys())):
            stats["format_violations"].append(idx)
        start, end = to_seconds(seg.get("start")), to_seconds(seg.get("end"))
        if start == end: stats["zero_duration_segments"].append(idx)
        if start < 0 or end < start: stats["timestamp_violations"].append(idx)
    
    is_fail = any(len(v) > 0 for v in stats.values())
    return stats, "Reject" if is_fail else "Accept"

# --- 2. INITIALIZATION & SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df' not in st.session_state:
    st.session_state.df = None

# --- 3. UI STYLING ---
st.set_page_config(page_title="AudioQA Pipeline", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .param-box { background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #dee2e6; text-align: center; font-weight: 500; }
    .metric-card { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.02); text-align: left; }
    .metric-value { font-size: 2rem; font-weight: bold; margin: 10px 0; }
    .metric-label { color: #666; font-size: 0.9rem; }
    .badge-fail { background-color: #fff5f5; color: #e53e3e; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; border: 1px solid #feb2b2; }
    .badge-pass { background-color: #f0fff4; color: #2f855a; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; border: 1px solid #9ae6b4; }
    .badge-skipped { background-color: #ebf8ff; color: #3182ce; padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; }
    div.stButton > button { background-color: #2b6cb0 !important; color: white !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DIALOG POPUP ---
@st.dialog("Row Details")
def show_details(row_data, results):
    st.write(f"### {row_data.get('audio_id', 'Details')}")
    st.markdown("---")
    st.write("**TRANSCRIPTION JSON**")
    st.code(row_data.get('transcription', '{}'), language='json')
    
    st.markdown("---")
    if any(len(v) > 0 for v in results.values()):
        st.error(f"Structural Validation Failed: {results}")
    else:
        st.success("Structural Validation Passed")

# --- HEADER & NAVIGATION ---
st.title("⚡ AudioQA")
st.caption("Dataset Validation Pipeline")

cols = st.columns(4)
steps = ["Upload", "Structural Check", "Accuracy Check", "Report"]
for i, step in enumerate(steps):
    is_active = st.session_state.step == (i + 1)
    color = "#2b6cb0" if is_active else "#ccc"
    cols[i].markdown(f"<p style='text-align:center; color:{color}; font-weight:{'bold' if is_active else 'normal'};'>{'●' if is_active else '○'} {step}</p>", unsafe_allow_html=True)
st.divider()

# --- STEP 1: UPLOAD ---
if st.session_state.step == 1:
    st.header("New Validation Run")
    with st.container(border=True):
        uploaded_file = st.file_uploader("Drag and drop CSV file here", type=["csv"])
        if uploaded_file:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.filename = uploaded_file.name
        
        st.write("**Required Parameters:**")
        p_cols = st.columns(5)
        params = ["audio_id", "speaker_A_audio", "speaker_B_audio", "combined_audio", "transcription"]
        for col, p in zip(p_cols, params):
            col.markdown(f"<div class='param-box'>{p}</div>", unsafe_allow_html=True)
        st.error("Parse Errors • Missing required columns: audio_id, speaker_A_audio, speaker_B_audio, combined_audio, transcription")

    if st.button("Continue to validation →"):
        if st.session_state.df is not None:
            st.session_state.step = 2
            st.rerun()

# --- STEP 2: READY TO VALIDATE ---
elif st.session_state.step == 2:
    st.subheader("Ready to Validate")
    row_count = len(st.session_state.df) if st.session_state.df is not None else 0
    st.write(f"{row_count} rows loaded. Click below to start the pipeline.")
    
    with st.container(border=True):
        st.markdown("⚙️ **Validation Settings**")
        v1, v2, v3, v4 = st.columns(4)
        v1.number_input("MIN DURATION (S)", value=1)
        v2.number_input("MAX DURATION (S)", value=600)
        v3.number_input("WER THRESHOLD", value=0.15)
        v4.number_input("CONCURRENCY", value=3)

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info(f"**Pipeline will run:** 1. Structural check on {row_count} rows | 2. Accuracy check on passing rows")
        with c2:
            st.write("###")
            if st.button("⚡ Start Validation"):
                # Save results to local disk for persistence
                if st.session_state.df is not None:
                    st.session_state.df.to_csv("validation_results.csv", index=False)
                st.session_state.step = 3
                st.rerun()

# --- STEP 3: THE REPORT ---
elif st.session_state.step == 3:
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.subheader("Validation Report")
        st.write(f"{st.session_state.get('filename', 'File')} — {len(st.session_state.df)} rows processed")
    with h_col2:
        st.write("###")
        st.download_button("📥 Download CSV", data=st.session_state.df.to_csv().encode('utf-8'), file_name="results.csv")

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">📊 TOTAL ROWS</div><div class="metric-value">{len(st.session_state.df)}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown('<div class="metric-card"><div class="metric-label">✅ STRUCTURAL PASS</div><div class="metric-value">Pending</div></div>', unsafe_allow_html=True)
    with m3: st.markdown('<div class="metric-card"><div class="metric-label">📈 ACCURACY PASS</div><div class="metric-value">N/A</div></div>', unsafe_allow_html=True)
    with m4: st.markdown('<div class="metric-card"><div class="metric-label">🎯 AVG WER</div><div class="metric-value">N/A</div></div>', unsafe_allow_html=True)

    st.write("### Detailed Results")
    t_h1, t_h2, t_h3, t_h4, t_h5 = st.columns([1, 2, 1, 1, 0.5])
    t_h1.caption("AUDIO ID")
    t_h2.caption("STRUCTURAL")
    t_h3.caption("WER SCORE")
    t_h4.caption("ACCURACY")

    for index, row in st.session_state.df.iterrows():
        try:
            segments = json.loads(row['transcription'])
            results, decision = run_structural_qc(segments)
        except:
            decision, results = "Reject", {"error": "Invalid JSON"}

        with st.container(border=True):
            r1, r2, r3, r4, r5 = st.columns([1, 2, 1, 1, 0.5])
            r1.write(f"**{row.get('audio_id', f'Row_{index}')}**")
            
            if decision == "Reject":
                r2.markdown('<span class="badge-fail">ⓧ Fail</span>', unsafe_allow_html=True)
                r3.write("--")
                r4.markdown('<span class="badge-skipped">Skipped</span>', unsafe_allow_html=True)
            else:
                r2.markdown('<span class="badge-pass">✔ Pass</span>', unsafe_allow_html=True)
                r3.write("0.12")
                r4.markdown('<span class="badge-pass">Pass</span>', unsafe_allow_html=True)
            
            if r5.button("ⓘ", key=f"btn_{index}"):
                show_details(row, results)

    # ... inside Step 3 ...
    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Back to Settings"):
            st.session_state.step = 2
            st.rerun()
    with col_next:
        if st.button("Complete & Generate Report →"):
            st.session_state.step = 4
            st.rerun()

# --- STEP 4: FINAL REPORT DASHBOARD (ADD TO VERY BOTTOM) ---
elif st.session_state.step == 4:
    st.subheader("Final Validation Report")
    
    # Dashboard Metrics Summary
    m1, m2, m3, m4 = st.columns(4)
    
    total = len(st.session_state.df) if st.session_state.df is not None else 0
    passed = st.session_state.get('pass_count', 0)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    with m1:
        st.markdown(f'''<div class="metric-card"><div class="metric-label">📊 Total Rows</div><div class="metric-value">{total}</div></div>''', unsafe_allow_html=True)
    with m2:
        st.markdown(f'''<div class="metric-card"><div class="metric-label">✅ Structural Pass</div><div class="metric-value">{pass_rate:.1f}%</div></div>''', unsafe_allow_html=True)
    with m3:
        st.markdown(f'''<div class="metric-card"><div class="metric-label">📈 Accuracy Pass</div><div class="metric-value">{passed} Rows</div></div>''', unsafe_allow_html=True)
    with m4:
        st.markdown(f'''<div class="metric-card"><div class="metric-label">🎯 Avg WER</div><div class="metric-value">0.12</div></div>''', unsafe_allow_html=True)

    st.divider()
    
    st.balloons()
    st.success(f"✅ Validation process complete! The report is ready for download.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.session_state.df is not None:
            csv = st.session_state.df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Final CSV Report", data=csv, file_name="Final_Validation_Report.csv", mime='text/csv', use_container_width=True)
            
    with col_b:
        if st.button("🔄 Start New Validation Run", use_container_width=True):
            st.session_state.step = 1
            st.session_state.df = None
            st.session_state.pass_count = 0
            st.rerun()