import streamlit as st
import pandas as pd
import json
import io

# --- 1. CORE LOGIC (From your Colab) ---
def to_seconds(ts):
    if not ts: return 0
    try:
        parts = list(map(float, str(ts).strip().split(':')))
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2: return parts[0] * 60 + parts[1]
        return float(parts[0])
    except: return 0

def run_structural_qc(segments):
    # Mandatory fields from your spreadsheet screenshot
    REQUIRED_KEYS = {"speaker", "start", "end", "text"}
    GAP_THRESHOLD = 5
    
    stats = {
        "format_violations": [],
        "timestamp_violations": [],
        "zero_duration_segments": [],
        "overlap_occurrences": [],
        "total_overlap_duration": 0,
        "large_gaps": []
    }

    last_end = 0
    for idx, seg in enumerate(segments):
        # A. Schema Validation
        current_keys = set(seg.keys())
        if not REQUIRED_KEYS.issubset(current_keys):
            missing = REQUIRED_KEYS - current_keys
            stats["format_violations"].append({"index": idx, "error": f"Missing: {missing}"})
            continue

        start = to_seconds(seg["start"])
        end = to_seconds(seg["end"])
        
        # B. Zero-Duration Check
        if start == end:
            stats["zero_duration_segments"].append({"index": idx, "timestamp": seg["start"], "text": seg.get("text", "")})

        # C. Logical Flow
        if start < 0 or (end < start):
            stats["timestamp_violations"].append({"index": idx, "range": f"{seg['start']} to {seg['end']}", "text": seg.get("text", "")})

        # D. Overlap & Gap
        if idx > 0:
            overlap = last_end - start
            if overlap > 0:
                stats["overlap_occurrences"].append({"index": idx, "seconds": round(overlap, 2)})
                stats["total_overlap_duration"] += overlap
            
            gap = start - last_end
            if gap > GAP_THRESHOLD:
                stats["large_gaps"].append({"index": idx, "seconds": round(gap, 2)})
        
        last_end = max(last_end, end)

    is_rejected = any([stats["format_violations"], stats["timestamp_violations"], stats["zero_duration_segments"]])
    decision = "Reject" if is_rejected else "Accept"
    return stats, decision

# --- 2. PAGE CONFIG & STYLES ---
st.set_page_config(page_title="AudioQA Pipeline", layout="wide")

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'results' not in st.session_state:
    st.session_state.results = None

st.markdown("""
    <style>
    .stButton>button { background-color: #2b6cb0; color: white; border-radius: 8px; width: 100%; }
    .param-box { background-color: #ffffff; color: #1a1a1a; padding: 10px; border-radius: 5px; border: 1px solid #dee2e6; text-align: center; font-weight: bold; }
    .stepper-active { color: #2b6cb0; font-weight: bold; border-bottom: 3px solid #2b6cb0; }
    .error-card { background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 10px; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & STEPPER ---
st.title("⚡ AudioQA")
st.caption("Dataset Validation Pipeline")

s1, s2, s3, s4 = st.columns(4)
with s1: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 1 else ''}'>✅ Upload</div>", unsafe_allow_html=True)
with s2: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 2 else ''}'>🔍 Structural Check</div>", unsafe_allow_html=True)
with s3: st.markdown(f"<div class='{'stepper-active' if st.session_state.step == 3 else ''}'>🎯 Accuracy Check</div>", unsafe_allow_html=True)
with s4: st.write("📊 Report")
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
        for col, p in zip(p_cols, ["audio_id", "speaker_A_audio", "speaker_B_audio", "combined_audio", "transcription"]):
            col.markdown(f"<div class='param-box'>{p}</div>", unsafe_allow_html=True)
        
        st.error("Parse Errors • Missing required columns: audio_id, speaker_A_audio, speaker_B_audio, combined_audio, transcription")

    if st.button("Continue to validation →"):
        if 'df' in st.session_state:
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("Please upload a CSV first.")

# --- STEP 2: READY TO VALIDATE ---
elif st.session_state.step == 2:
    st.subheader("Ready to Validate")
    st.write(f"{len(st.session_state.df)} rows loaded. Click below to start.")
    
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
            # Execute logic
            segments = st.session_state.df.to_dict(orient='records')
            results, decision = run_structural_qc(segments)
            st.session_state.results = results
            st.session_state.decision = decision
            st.session_state.step = 3
            st.rerun()

# --- STEP 3: STRUCTURAL QC RESULTS ---
elif st.session_state.step == 3:
    res = st.session_state.results
    dec = st.session_state.decision
    
    st.subheader(f"Structural QC Audit: {st.session_state.filename}")
    
    # AI Verdict Style (Manual for now, can add Gemini later)
    col_v1, col_v2 = st.columns(2)
    col_v1.metric("Verdict", dec)
    col_v1.progress(0.4 if dec == "Reject" else 1.0)
    
    st.write("### ERROR QUANTIFICATION")
    q1, q2, q3, q4 = st.columns(4)
    q1.markdown(f"**Format Violations**\n### {len(res['format_violations'])}")
    q2.markdown(f"**Timestamp Violations**\n### {len(res['timestamp_violations'])}")
    q3.markdown(f"**Zero-Duration**\n### {len(res['zero_duration_segments'])}")
    q4.markdown(f"**Overlap Count**\n### {len(res['overlap_occurrences'])}")

    st.divider()
    st.write("### FLAGGED SEGMENTS (ACTION REQUIRED)")
    
    if not any([res['format_violations'], res['timestamp_violations'], res['zero_duration_segments']]):
        st.success("No critical structural issues found.")
    else:
        for item in res['timestamp_violations']:
            st.markdown(f"<div class='error-card'>⚠️ <b>TIMESTAMP ERROR [Idx {item['index']}]:</b> Range {item['range']}<br><small>{item['text']}</small></div>", unsafe_allow_html=True)
        
        for item in res['overlap_occurrences']:
            st.markdown(f"<div class='error-card'>🟠 <b>OVERLAP DETECTED [Idx {item['index']}]:</b> {item['seconds']}s overlap</div>", unsafe_allow_html=True)

    if st.button("← Back to Settings"):
        st.session_state.step = 2
        st.rerun()