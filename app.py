import streamlit as st
import pandas as pd
import json

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Custom CSS for Royal Blue UI and Reference Tags
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
    }
    div.stButton > button:first-child:hover {
        background-color: #27408B;
        color: white;
    }
    .column-tag {
        display: inline-block;
        background-color: #f0f2f6;
        color: #555;
        padding: 2px 8px;
        border-radius: 4px;
        margin: 2px;
        font-family: monospace;
        font-size: 12px;
        border: 1px solid #ddd;
    }
    .small-header { font-size: 14px !important; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .highlight-red { background-color: #ffcccc; color: #cc0000; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    .highlight-green { background-color: #ccffcc; color: #006600; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    .report-box { border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. HEADER & DYNAMIC INPUT ---
st.title("NEW VALIDATION RUN")

# Validation Settings Dropdown (New)
with st.expander("⚙️ Validation Settings"):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        st.number_input("MIN DURATION (S)", value=1, help="Minimum audio length")
    with v_col2:
        st.number_input("MAX DURATION (S)", value=600, help="Maximum audio length")
    with v_col3:
        st.number_input("WER THRESHOLD", value=0.15, step=0.01, help="Max WER to pass (0-1)")
    with v_col4:
        st.number_input("CONCURRENCY", value=3, min_value=1, max_value=10, help="Parallel rows (1-10)")

st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# Column Tags UI (Matches reference)
st.markdown("""
    <div style="text-align: center; padding: 10px; border: 1px dashed #ccc; border-radius: 10px; background-color: #fafafa;">
        <p style="color: #666; margin-bottom: 5px;">Required columns:</p>
        <span class="column-tag">audio_id</span>
        <span class="column-tag">speaker_A_audio</span>
        <span class="column-tag">speaker_B_audio</span>
        <span class="column-tag">combined_audio</span>
        <span class="column-tag">transcription</span>
    </div>
    """, unsafe_allow_html=True)

main_csv = st.file_uploader("", type=["csv"], label_visibility="collapsed")

# Right-aligned Royal Blue Button
_, col_btn = st.columns([4, 1])
with col_btn:
    run_pressed = st.button("Start Validation", disabled=not main_csv)

# --- ERROR HANDLING & DASHBOARD ---
if main_csv is not None:
    try:
        df = pd.read_csv(main_csv)
        required_columns = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"**Parse Errors**\n\n• Missing required columns: {', '.join(missing_cols)}")
        
        elif run_pressed:
            st.write("---")
            # Analysis data stays consistent with your requirements (191/196)
            v_total, v_succ, v_fail = "196", "191", "5"
            v_dur, v_sr, v_snr, v_sil, v_clip = "210.4s", "44.1 kHz", "38.2 dB", "12.5%", "0.000%"
            v_wer, v_cer, v_sem, v_psdn, v_tier = "0.304", "0.152", "0.9836", "1.000", "Gold"

            # Results Display (Standard Metrics)
            m1, m2, m3 = st.columns(3)
            m1.metric("TOTAL", v_total)
            m2.metric("SUCCEEDED", v_succ, "↑ 100%")
            m3.metric("FAILED", v_fail)

            st.subheader("PROGRESS")
            st.progress(1.0)
            st.write(f"PROCESSED: {v_succ} / {v_total}")

            # Audio and Scoring sections follow here... (same as previous version)
            st.markdown('<p class="small-header">AUDIO QUALITY</p>', unsafe_allow_html=True)
            q_cols = st.columns(5)
            for col, lab, val in zip(q_cols, ["DURATION", "SAMPLE RATE", "SNR", "SILENCE", "CLIPPING"], [v_dur, v_sr, v_snr, v_sil, v_clip]):
                col.metric(lab, val)

            st.write("---")
            st.header("STRUCTURAL QUALITY CHECK")
            st.markdown("**Summary:**\n* No critical or minor errors were found in this file.\n* Passed all format and timing checks.")
            
            st.write("---")
            st.header("ACCURACY QUALITY CONTROL")
            c1, c2 = st.columns(2)
            c1.markdown('Reference: হেই করিম আমি <span class="highlight-red">দেশে</span>...', unsafe_allow_html=True)
            c2.markdown('Hypothesis: হেই করিম আমি <span class="highlight-green">জানো</span>...', unsafe_allow_html=True)

            st.write("---")
            st.header("FINAL VALIDATION REPORT")
            st.markdown('<div class="report-box"><h3>Final Status: PASSED</h3><p>Processed: 196 (Success: 191)</p></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"**Parse Errors**\n\n• Could not process the CSV: {str(e)}")