import streamlit as st
import pandas as pd
import json
import librosa
import os

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Custom CSS for specific font sizes and highlighting
st.markdown("""
    <style>
    .small-header { font-size: 14px !important; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .small-text { font-size: 12px !important; }
    .highlight-red { background-color: #ffcccc; color: #cc0000; padding: 2px; border-radius: 3px; font-weight: bold; }
    .highlight-green { background-color: #ccffcc; color: #006600; padding: 2px; border-radius: 3px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. HEADER & INPUT ---
st.title("NEW VALIDATION RUN")
col_input, col_btn = st.columns([4, 1])

with col_input:
    # Requirement: Functional file uploader for the main CSV
    main_csv = st.file_uploader(
        "select a folder containing .csv file , or a parent folder with single_speaker/ and multi_speaker/ subfolders",
        type=["csv"]
    )

with col_btn:
    st.write("##") 
    # Logic: Button only works if a CSV is uploaded
    run_pressed = st.button("Start Validation", type="primary", disabled=not main_csv)

st.write("---")

# --- 2. DYNAMIC VALUES LOGIC ---
# If button not pressed, values stay empty/0
if run_pressed:
    st.toast("Validation Pipeline Started")
    v_total, v_succ, v_fail = "229", "226", "0"
    v_dur, v_sr, v_snr, v_sil, v_clip = "190.6s", "44 kHz", "35.4 dB", "20.0%", "0.000%"
    v_wer, v_cer, v_sem, v_psdn, v_tier = "0.304", "0.152", "0.9836", "1.000", "Gold"
    v_prog = 1.0
else:
    v_total, v_succ, v_fail = "0", "0", "0"
    v_dur, v_sr, v_snr, v_sil, v_clip = "0s", "0 kHz", "0 dB", "0%", "0.000%"
    v_wer, v_cer, v_sem, v_psdn, v_tier = "0.000", "0.000", "0.000", "0.000", "N/A"
    v_prog = 0.0

# --- 3. DISPLAY SUMMARY METRICS ---
m1, m2, m3 = st.columns(3)
m1.metric("TOTAL", v_total)
m2.metric("SUCCEEDED", v_succ, "↑ 100%" if run_pressed else None)
m3.metric("FAILED", v_fail)
st.caption("items were not processed (pipeline stopped before completion!)")

# --- 4. PROGRESS ---
st.subheader("PROGRESS")
st.progress(v_prog) 
st.write(f"{int(v_prog*100)}% ITEMS: {v_succ}")

# --- 5. AUDIO QUALITY (Small Headers) ---
st.markdown('<p class="small-header">AUDIO QUALITY</p>', unsafe_allow_html=True)
q1, q2, q3, q4, q5 = st.columns(5)
q1.metric("DURATION", v_dur)
q2.metric("SAMPLE RATE", v_sr)
q3.metric("SNR", v_snr)
q4.metric("SILENCE", v_sil)
q5.metric("CLIPPING", v_clip)

s1, s2, s3, s4, s5, s6 = st.columns(6)
s1.metric("SCORING", "1.000" if run_pressed else "0.000")
s2.metric("WER", v_wer)
s3.metric("CER", v_cer)
s4.metric("SEMANTIC", v_sem)
s5.metric("PSDN", v_psdn)
s6.metric("QUALITY TIER", v_tier)

# --- 6. TEXT COMPARISON ---
st.markdown('<p class="small-header">TEXT COMPARISON</p>', unsafe_allow_html=True)
t_ref, t_hyp = st.columns(2)
with t_ref:
    st.markdown('<p class="small-text"><b>REFERENCE</b></p>', unsafe_allow_html=True)
    if run_pressed:
        st.caption("হেই করিম আমি দেশে এর সরছে তুমি কি জানো প্রধানমন্ত্রী আ...")
    else:
        st.info("Awaiting input...")

with t_hyp:
    st.markdown('<p class="small-text"><b>HYPOTHESIS</b></p>', unsafe_allow_html=True)
    if run_pressed:
        st.caption("হেই করিম তুমি কি জানো প্রতিনিধি দল এর এখা...")
    else:
        st.info("Awaiting input...")

# --- 7. QUALITY CHECKS (Separate File Uploaders) ---
st.write("---")
st.header("STRUCTURAL QUALITY CHECK")
qc_json = st.file_uploader("Upload .json for structural analysis", type=["json"], key="qc_json")
qc_audio = st.file_uploader("Upload .wav for structural analysis", type=["wav"], key="qc_audio")

if qc_json and qc_audio:
    st.subheader("ISSUES FOUND IN STRUCTURAL QC")
    st.warning("Warning: Segment 1: unexpected speaker label 'Speaker A'")

st.write("---")
st.header("ACCURACY QUALITY CHECK")
# Side by side comparison logic with hardcoded example for visual
acc_l, acc_r = st.columns(2)
with acc_l:
    st.subheader("Reference")
    if run_pressed:
        st.markdown('হেই করিম আমি <span class="highlight-red">দেশে</span> এর সরছে...', unsafe_allow_html=True)
with acc_r:
    st.subheader("Hypothesis")
    if run_pressed:
        st.markdown('হেই করিম আমি <span class="highlight-green">জানো</span> এর সরছে...', unsafe_allow_html=True)