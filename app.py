import streamlit as st
import pandas as pd

# --- 1. INITIALIZATION (MUST BE AT THE TOP) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df' not in st.session_state:
    st.session_state.df = None

# --- 2. CORE LOGIC ---
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
        # Check if keys are missing
        if not REQUIRED_KEYS.issubset(current_keys):
            missing = REQUIRED_KEYS - current_keys
            stats["format_violations"].append({"index": idx, "error": f"Missing: {missing}"})
            continue # This now works correctly without checking st.session_state
            
        start = to_seconds(seg["start"])
        end = to_seconds(seg["end"])
        if start >= end:
            stats["timestamp_violations"].append({"index": idx, "error": "End time before start time"})
            
    decision = "Reject" if any(stats.values()) else "Accept"
    return stats, decision

# --- 3. UI STYLING ---
st.set_page_config(page_title="AudioQA Pipeline", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .badge-fail { background-color: #fff5f5; color: #e53e3e; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; border: 1px solid #feb2b2; }
    .badge-skipped { background-color: #ebf8ff; color: #3182ce; padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. STEPPER NAVIGATION ---
st.title("⚡ AudioQA")
s1, s2, s3, s4 = st.columns(4)
# Logic to show active step based on st.session_state.step
with s1: st.write("✅ Upload" if st.session_state.step > 1 else "**Upload**")
with s2: st.write("✅ Structural" if st.session_state.step > 2 else "**Structural Check**" if st.session_state.step == 2 else "Structural Check")
with s3: st.write("**Accuracy Check**" if st.session_state.step == 3 else "Accuracy Check")
with s4: st.write("Report")
st.divider()

# --- PAGE 1: UPLOAD ---
if st.session_state.step == 1:
    st.header("New Validation Run")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file)
    
    if st.button("Continue →"):
        if st.session_state.df is not None:
            st.session_state.step = 2
            st.rerun()

# --- PAGE 2: SETTINGS ---
elif st.session_state.step == 2:
    st.subheader("Ready to Validate")
    if st.button("⚡ Start Validation"):
        results, decision = run_structural_qc(st.session_state.df.to_dict(orient='records'))
        st.session_state.results = results
        st.session_state.decision = decision
        st.session_state.step = 3
        st.rerun()

# --- PAGE 3: REPORT ---
elif st.session_state.step == 3:
    st.subheader("Validation Report")
    # Show the results table here matching your reference images
    for index, row in st.session_state.df.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 4, 1])
            col1.write(f"**{row.get('audio_id', index)}**")
            col2.markdown('<span class="badge-fail">ⓧ Fail</span>', unsafe_allow_html=True)
            col3.markdown('<span class="badge-skipped">Skipped</span>', unsafe_allow_html=True)