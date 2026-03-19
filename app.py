import streamlit as st
import pandas as pd

# --- 1. CORE LOGIC ---
def to_seconds(ts):
    if not ts: return 0
    try:
        parts = list(map(float, str(ts).strip().split(':')))
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2: return parts[0] * 60 + parts[1]
        return float(parts[0])
    except: return 0

def run_structural_qc(segments):
    REQUIRED_KEYS = {"speaker", "start", "end", "text"}
    stats = {"format_violations": [], "timestamp_violations": [], "zero_duration_segments": [], "overlap_occurrences": []}
    
    for idx, seg in enumerate(segments):
        current_keys = set(seg.keys())
        if not REQUIRED_KEYS.issubset(current_keys):
            stats["format_violations"].append({"index": idx, "error": "Missing required columns"})
    
    # Simple rejection logic for UI testing
    decision = "Reject" if len(stats["format_violations"]) > 0 else "Accept"
    return stats, decision

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="AudioQA Pipeline", layout="wide")

if 'step' not in st.session_state:
    st.session_state.step = 1

st.markdown("""
    <style>
    .stButton>button { background-color: #2b6cb0; color: white; border-radius: 8px; width: 100%; }
    .param-box { background-color: #ffffff; color: #1a1a1a; padding: 10px; border-radius: 5px; border: 1px solid #dee2e6; text-align: center; font-weight: bold; }
    .stepper-active { color: #2b6cb0; font-weight: bold; border-bottom: 3px solid #2b6cb0; text-align: center;}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & STEPPER ---
st.title("⚡ AudioQA")
s1, s2, s3, s4 = st.columns(4)
with s1: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 1 else ''}'>Upload</div>", unsafe_allow_html=True)
with s2: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 2 else ''}'>Structural Check</div>", unsafe_allow_html=True)
with s3: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 3 else ''}'>Accuracy Check</div>", unsafe_allow_html=True)
with s4: st.markdown("<div>Report</div>", unsafe_allow_html=True)
st.divider()

# --- PAGE 1: UPLOAD ---
if st.session_state.step == 1:
    st.header("New Validation Run")
    with st.container(border=True):
        uploaded_file = st.file_uploader("Drag and drop CSV file here", type=["csv"])
        if uploaded_file:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.filename = uploaded_file.name
        
        st.write("**Required Parameters:**")
        p_cols = st.columns(5)
        for col, p in zip(p_cols, ["audio_id", "speaker_A_audio", "speaker_B_audio", "combined_audio", "transcription"]):
            col.markdown(f"<div class='param-box'>{p}</div>", unsafe_allow_html=True)
        st.error("Parse Errors • Missing required columns: audio_id, speaker_A_audio, speaker_B_audio, combined_audio, transcription")

    if st.button("Continue to validation →"):
        if 'df' in st.session_state:
            st.session_state.step = 2
            st.rerun()

# --- PAGE 2: READY TO VALIDATE ---
elif st.session_state.step == 2:
    st.subheader("Ready to Validate")
    st.write(f"{len(st.session_state.df)} rows loaded from {st.session_state.get('filename', 'file')}")
    
    with st.container(border=True):
        st.markdown("⚙️ **Validation Settings**")
        v1, v2, v3, v4 = st.columns(4)
        v1.number_input("MIN DURATION (S)", value=1)
        v2.number_input("MAX DURATION (S)", value=600)
        v3.number_input("WER THRESHOLD", value=0.15)
        v4.number_input("CONCURRENCY", value=3)

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        c1.info("**Pipeline will run:** 1. Structural check | 2. Accuracy check")
        if c2.button("⚡ Start Validation"):
            results, decision = run_structural_qc(st.session_state.df.to_dict(orient='records'))
            st.session_state.results = results
            st.session_state.decision = decision
            st.session_state.step = 3
            st.rerun()

# --- PAGE 3: REPORT ---
elif st.session_state.step == 3:
    st.subheader("Validation Report")
    
    # Dashboard Cards
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Total Rows", len(st.session_state.df))
    t2.metric("Structural Pass", "0.0%" if st.session_state.decision == "Reject" else "100%")
    t3.metric("Accuracy Pass", "N/A")
    t4.metric("Avg WER", "N/A")

    st.write("### Detailed Results")
    for index, row in st.session_state.df.iterrows():
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([1, 4, 1])
            col_a.write(f"**{row.get('audio_id', index)}**")
            col_b.error("🔴 Fail: Speaker A audio: Invalid WAV header: expected 'RIFF', got 'ID3'")
            col_c.info("Skipped")

    if st.button("← Back to Settings"):
        st.session_state.step = 2
        st.rerun()