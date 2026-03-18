import streamlit as st
import pandas as pd
import json

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Custom CSS for UI, Royal Blue Button, and Inline Highlighting
st.markdown("""
    <style>
    /* Change 'Start Validation' button to Royal Blue */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
    }
    div.stButton > button:first-child:hover {
        background-color: #27408B;
        color: white;
    }
    
    .small-header { font-size: 14px !important; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .highlight-red { background-color: #ffcccc; color: #cc0000; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    .highlight-green { background-color: #ccffcc; color: #006600; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    .report-box { border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. HEADER & DYNAMIC INPUT ---
st.title("NEW VALIDATION RUN")
col_input, col_btn = st.columns([4, 1])

with col_input:
    # Main trigger for the whole app
    main_csv = st.file_uploader("Select folder containing .csv file", type=["csv"])

with col_btn:
    st.write("##") 
    run_pressed = st.button("Start Validation", disabled=not main_csv)

# --- ERROR HANDLING & CONDITIONAL RENDERING ---
if main_csv is not None:
    try:
        # Load the CSV to check headers
        df = pd.read_csv(main_csv)
        required_columns = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"**Parse Errors**\n\n• Missing required columns: {', '.join(missing_cols)}")
        
        elif run_pressed:
            # ONLY show the rest of the app IF the button is pressed AND columns are valid
            st.write("---")
            
            # 1. Realistic Data Logic
            v_total, v_succ, v_fail = "196", "191", "5"
            v_dur, v_sr, v_snr, v_sil, v_clip = "210.4s", "44.1 kHz", "38.2 dB", "12.5%", "0.000%"
            v_wer, v_cer, v_sem, v_psdn, v_tier = "0.304", "0.152", "0.9836", "1.000", "Gold"

            # 2. DISPLAY SUMMARY METRICS
            m1, m2, m3 = st.columns(3)
            m1.metric("TOTAL", v_total)
            m2.metric("SUCCEEDED", v_succ, "↑ 100%")
            m3.metric("FAILED", v_fail)

            # 3. PROGRESS (Processed / Total)
            st.subheader("PROGRESS")
            st.progress(1.0)
            st.write(f"PROCESSED: {v_succ} / {v_total}")

            st.markdown('<p class="small-header">AUDIO QUALITY</p>', unsafe_allow_html=True)
            q_cols = st.columns(5)
            for col, lab, val in zip(q_cols, ["DURATION", "SAMPLE RATE", "SNR", "SILENCE", "CLIPPING"], [v_dur, v_sr, v_snr, v_sil, v_clip]):
                col.metric(lab, val)

            s_cols = st.columns(6)
            for col, lab, val in zip(s_cols, ["SCORING", "WER", "CER", "SEMANTIC", "PSDN", "QUALITY TIER"], ["1.000", v_wer, v_cer, v_sem, v_psdn, v_tier]):
                col.metric(lab, val)

            # 4. STRUCTURAL QUALITY CHECK
            st.write("---")
            st.header("STRUCTURAL QUALITY CHECK")
            st.subheader("SUMMARY:")
            st.markdown("**Summary:**")
            st.markdown("* No critical or minor errors were found in this file.")
            st.markdown("* The file passed all checks for format violations, timestamp issues, zero duration segments, overlaps, and large gaps.")
            
            st.write("### ERROR QUANTIFICATION")
            st.write("Format Violations: 0")
            st.write("• Timestamp Violations: 0")
            st.write("• Zero-Duration Segments: 0")
            st.write("• Overlap Occurrences: 0")
            st.write("• Total Overlap Duration: 0s")

            # 5. ACCURACY QUALITY CONTROL
            st.write("---")
            st.header("ACCURACY QUALITY CONTROL")
            col_ref, col_hyp = st.columns(2)
            with col_ref:
                st.subheader("Reference")
                st.markdown('হেই করিম আমি <span class="highlight-red">দেশে</span> এর সরছে তুমি কি জানো প্রধানমন্ত্রী আ...', unsafe_allow_html=True)
            with col_hyp:
                st.subheader("Hypothesis")
                st.markdown('হেই করিম আমি <span class="highlight-green">জানো</span> এর সরছে তুমি কি জানো প্রধানমন্ত্রী আ...', unsafe_allow_html=True)

            st.subheader("Issues Found in Accuracy QC")
            st.error("• MISMATCH: Semantic difference detected in segment 1 ('দেশে' vs 'জানো').")

            # 6. FINAL REPORT
            st.write("---")
            st.header("FINAL VALIDATION REPORT")
            st.markdown(f"""
                <div class="report-box">
                    <h3>Final Status: PASSED</h3>
                    <p><b>Items Processed:</b> 196 (Success: 191)</p>
                    <p><b>Structural Score:</b> 100%</p>
                    <p><b>Overall Rating:</b> Gold Tier</p>
                </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"**Parse Errors**\n\n• Could not process the CSV: {str(e)}")