import streamlit as st
import pandas as pd
import json

# --- 1. CORE LOGIC & CONFIGURATION ---
REQUIRED_KEYS = {"start", "end", "speaker", "text"} # Mandatory Fields
GAP_THRESHOLD = 5

def to_seconds(ts):
    if not ts: return 0
    try:
        parts = list(map(float, str(ts).strip().split(':')))
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2: return parts[0] * 60 + parts[1]
        return float(parts[0])
    except: return 0

def run_structural_qc(segments):
    """Core logic implementation from your script"""
    stats = {
        "format_violations": [],
        "timestamp_violations": [],
        "zero_duration_segments": [],
        "overlap_occurrences": [],
        "total_overlap_duration": 0
    }
    
    last_end = 0
    for idx, seg in enumerate(segments):
        # A. Mandatory Schema Validation
        current_keys = set(seg.keys())
        if not REQUIRED_KEYS.issubset(current_keys):
            missing = REQUIRED_KEYS - current_keys
            stats["format_violations"].append({"index": idx, "error": f"Missing: {list(missing)}"})
            continue

        start = to_seconds(seg.get("start"))
        end = to_seconds(seg.get("end"))
        
        # B. Zero-Duration Check
        if start == end:
            stats["zero_duration_segments"].append({"index": idx, "timestamp": seg["start"]})

        # C. Logical Flow
        if start < 0 or (end < start):
            stats["timestamp_violations"].append({"index": idx, "range": f"{seg['start']} to {seg['end']}"})

        # D. Overlap Detection
        if idx > 0:
            overlap = last_end - start
            if overlap > 0:
                stats["overlap_occurrences"].append({"index": idx, "seconds": round(overlap, 2)})
                stats["total_overlap_duration"] += overlap
        
        last_end = max(last_end, end)

    # Decision Matrix
    is_fail = any([stats["format_violations"], stats["timestamp_violations"], stats["zero_duration_segments"]])
    decision = "Reject" if is_fail else "Accept"
    return stats, decision

# --- 2. STREAMLIT INITIALIZATION ---
st.set_page_config(page_title="AudioQA Pipeline", layout="wide")

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'df' not in st.session_state:
    st.session_state.df = None

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    .param-box { background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #dee2e6; text-align: center; font-weight: 500; }
    .badge-fail { background-color: #fff5f5; color: #e53e3e; padding: 2px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #feb2b2; }
    .badge-pass { background-color: #f0fff4; color: #2f855a; padding: 2px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #9ae6b4; }
    .stButton>button { background-color: #2b6cb0; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & STEPPER ---
st.title("⚡ AudioQA")
cols = st.columns(4)
steps = ["Upload", "Structural Check", "Accuracy Check", "Report"]
for i, s in enumerate(steps):
    label = f"✅ {s}" if st.session_state.step > i+1 else f"**{i+1}. {s}**" if st.session_state.step == i+1 else f"{i+1}. {s}"
    cols[i].write(label)
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
        
        st.error("**Parse Errors** • Missing required columns: audio_id, speaker_A_audio, speaker_B_audio, combined_audio, transcription")

    if st.button("Continue to validation →"):
        if st.session_state.df is not None:
            st.session_state.step = 2
            st.rerun()

# --- STEP 2: READY TO VALIDATE ---
elif st.session_state.step == 2:
    st.subheader("Ready to Validate")
    st.write(f"{len(st.session_state.df)} rows loaded. Click below to start the pipeline.")
    
    with st.container(border=True):
        st.markdown("⚙️ **Validation Settings**")
        v1, v2, v3, v4 = st.columns(4)
        v1.number_input("MIN DURATION (S)", value=1)
        v2.number_input("MAX DURATION (S)", value=600)
        v3.number_input("WER THRESHOLD", value=0.15)
        v4.number_input("CONCURRENCY", value=3)

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        c1.info(f"**Pipeline will run:** 1. Structural check on all {len(st.session_state.df)} rows | 2. Accuracy check on passing rows")
        if c2.button("⚡ Start Validation"):
            st.session_state.step = 3
            st.rerun()

# --- STEP 3: STRUCTURE CHECK (CORE LOGIC) ---
elif st.session_state.step == 3:
    st.subheader(f"Structural QC Audit: {st.session_state.get('filename', '')}")
    
    for index, row in st.session_state.df.iterrows():
        # RUN ACTUAL LOGIC
        try:
            raw_json = json.loads(row['transcription'])
            results, decision = run_structural_qc(raw_json)
        except Exception as e:
            decision, results = "Reject", {"format_violations": [{"error": "Invalid JSON format"}]}

        with st.container(border=True):
            r1, r2, r3, r4 = st.columns([1, 3, 1, 0.5])
            r1.write(f"**{row['audio_id']}**")
            
            if decision == "Reject":
                r2.markdown('<span class="badge-fail">Reject</span>', unsafe_allow_html=True)
                err_summary = []
                if results.get('format_violations'): err_summary.append(f"{len(results['format_violations'])} Schema Errors")
                if results.get('timestamp_violations'): err_summary.append("Logic/Timestamp Errors")
                r2.caption(" | ".join(err_summary))
            else:
                r2.markdown('<span class="badge-pass">Accept</span>', unsafe_allow_html=True)
            
            r3.write("Skipped" if decision == "Reject" else "Pending...")
            if r4.button("ⓘ", key=f"btn_{index}"):
                st.toast(f"Detailed results for {row['audio_id']} generated.")

    if st.button("← Back to Settings"):
        st.session_state.step = 2
        st.rerun()