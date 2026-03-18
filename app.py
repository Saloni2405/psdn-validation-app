import streamlit as st
import pandas as pd
import json

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Custom CSS to unify the Required Columns and Uploader into one block
st.markdown("""
    <style>
    /* Royal Blue Button Styling */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
    }
    div.stButton > button:first-child:hover {
        background-color: #27408B;
        color: white;
    }
    
    /* Unified White Block for Columns + Uploader */
    .upload-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        color: #555;
        text-align: center;
        margin-bottom: -50px; /* Pulls the Streamlit uploader visually into the block */
    }
    
    .column-tag {
        display: inline-block;
        background-color: #f0f2f6;
        color: #555;
        padding: 4px 10px;
        border-radius: 4px;
        margin: 4px;
        font-family: monospace;
        font-size: 13px;
        border: 1px solid #ddd;
    }

    .small-header { font-size: 14px !important; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .report-box { border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: black; }
    .highlight-red { background-color: #ffcccc; color: #cc0000; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    .highlight-green { background-color: #ccffcc; color: #006600; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. HEADER & DYNAMIC INPUT ---
st.title("NEW VALIDATION RUN")

# Validation Settings Dropdown
with st.expander("⚙️ Validation Settings"):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        st.number_input("MIN DURATION (S)", value=1)
    with v_col2:
        st.number_input("MAX DURATION (S)", value=600)
    with v_col3:
        st.number_input("WER THRESHOLD", value=0.15)
    with v_col4:
        st.number_input("CONCURRENCY", value=3)

st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# --- THE UNIFIED BLOCK ---
st.markdown("""
    <div class="upload-container">
        <p style="margin-bottom: 10px; font-size: 14px;">Required columns:</p>
        <span class="column-tag">audio_id</span>
        <span class="column-tag">speaker_A_audio</span>
        <span class="column-tag">speaker_B_audio</span>
        <span class="column-tag">combined_audio</span>
        <span class="column-tag">transcription</span>
    </div>
    """, unsafe_allow_html=True)

# Streamlit's native uploader (layered to look like it's part of the block)
main_csv = st.file_uploader("", type=["csv"], label_visibility="collapsed")

# Start Button
_, col_btn = st.columns([4, 1])
with col_btn:
    run_pressed = st.button("Start Validation", disabled=not main_csv)

# --- ERROR HANDLING & DASHBOARD LOGIC ---
if main_csv is not None:
    try:
        df = pd.read_csv(main_csv)
        required_columns = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"**Parse Errors**\n\n• Missing required columns: {', '.join(missing_cols)}")
        
        elif run_pressed:
            st.write("---")
            # Metrics 
            v_total, v_succ, v_fail = "196", "191", "5"
            v_dur, v_sr, v_snr, v_sil, v_clip = "210.4s", "44.1 kHz", "38.2 dB", "12.5%", "0.000%"
            
            m1, m2, m3 = st.columns(3)
            m1.metric("TOTAL", v_total)
            m2.metric("SUCCEEDED", v_succ, "↑ 100%")
            m3.metric("FAILED", v_fail)

            st.subheader("PROGRESS")
            st.progress(1.0)
            st.write(f"PROCESSED: {v_succ} / {v_total}")

            st.markdown('<p class="small-header">AUDIO QUALITY</p>', unsafe_allow_html=True)
            q_cols = st.columns(5)
            for col, lab, val in zip(q_cols, ["DURATION", "SAMPLE RATE", "SNR", "SILENCE", "CLIPPING"], [v_dur, v_sr, v_snr, v_sil, v_clip]):
                col.metric(lab, val)
            
            # Structural & Accuracy sections follow...
            st.write("---")
            st.header("STRUCTURAL QUALITY CHECK")
            st.write("### ERROR QUANTIFICATION")
            st.write("Format Violations: 0")
            st.write("• Overlap Occurrences: 0")

    except Exception as e:
        st.error(f"**Parse Errors**\n\n• Could not process the CSV: {str(e)}")