import streamlit as st
import pandas as pd

# 1. INITIALIZATION (Must be the very first thing after imports)
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df' not in st.session_state:
    st.session_state.df = None

# --- CORE LOGIC ---
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
    stats = {"format_violations": [], "timestamp_violations": []}
    for idx, seg in enumerate(segments):
        if not REQUIRED_KEYS.issubset(set(seg.keys())):
            stats["format_violations"].append({"index": idx, "error": "Missing Keys"})
    decision = "Reject" if stats["format_violations"] else "Accept"
    return stats, decision

# --- UI STYLING ---
st.set_page_config(page_title="AudioQA Pipeline", layout="wide")

st.markdown("""
    <style>
    .badge-fail { background-color: #fff5f5; color: #e53e3e; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #feb2b2; }
    .badge-skipped { background-color: #ebf8ff; color: #3182ce; padding: 4px 12px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- STEPPER ---
st.title("⚡ AudioQA")
s1, s2, s3, s4 = st.columns(4)
with s1: st.write("✅ Upload" if st.session_state.step > 1 else "**1. Upload**")
with s2: st.write("**2. Structural**" if st.session_state.step == 2 else "2. Structural")
with s3: st.write("**3. Report**" if st.session_state.step == 3 else "3. Report")
st.divider()

# --- NAVIGATION LOGIC ---

# PAGE 1
if st.session_state.step == 1:
    st.header("Upload Dataset")
    uploaded_file = st.file_uploader("Choose CSV", type="csv")
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file)
        if st.button("Continue"):
            st.session_state.step = 2
            st.rerun()

# PAGE 2
elif st.session_state.step == 2:
    st.header("Ready to Validate")
    if st.button("Start Validation"):
        results, decision = run_structural_qc(st.session_state.df.to_dict(orient='records'))
        st.session_state.results = results
        st.session_state.decision = decision
        st.session_state.step = 3
        st.rerun()

# PAGE 3
elif st.session_state.step == 3:
    st.subheader("Validation Report")
    # Using your shared Modal logic
    @st.dialog("Row Details")
    def show_details(row, idx):
        st.write(f"Details for {row.get('audio_id', idx)}")
        st.error("Structural Error: Invalid WAV Header")

    for index, row in st.session_state.df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 2, 1, 0.5])
            c1.write(f"**{row.get('audio_id', index)}**")
            c2.markdown('<span class="badge-fail">ⓧ Fail</span>', unsafe_allow_html=True)
            c3.markdown('<span class="badge-skipped">Skipped</span>', unsafe_allow_html=True)
            if c4.button("ⓘ", key=f"btn_{index}"):
                show_details(row, index)

    if st.button("← Back"):
        st.session_state.step = 2
        st.rerun()