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
    .small-header { font-size: 16px !important; font-weight: bold; margin-bottom: 5px; }
    .small-text { font-size: 13px !important; line-height: 1.4; }
    .highlight-red { background-color: #ffcccc; padding: 2px 4px; border-radius: 3px; color: #cc0000; font-weight: bold; }
    .highlight-green { background-color: #ccffcc; padding: 2px 4px; border-radius: 3px; color: #006600; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & INPUT ---
st.title("NEW VALIDATION RUN")
col_input, col_btn = st.columns([4, 1])
with col_input:
    # Requirement 1: Specific folder instruction [cite: 3, 4]
    st.text_input("Input Source", 
                 placeholder="select a folder containing .csv file , or a parent folder with single_speaker/ and multi_speaker/ subfolders")
with col_btn:
    st.write("##") 
    if st.button("Start Validation", type="primary"):
        st.toast("Validation Pipeline Started")

st.write("---")

# --- SUMMARY METRICS ---
m1, m2, m3 = st.columns(3)
m1.metric("TOTAL", "229") # [cite: 9]
m2.metric("SUCCEEDED", "226", "↑ 100%") # [cite: 11]
m3.metric("FAILED", "0") # [cite: 13]
st.caption("items were not processed (pipeline stopped before completion!)") # [cite: 12]

# --- PROGRESS ---
st.subheader("PROGRESS")
st.progress(1.0) 
st.write("100% ITEMS: 225") # [cite: 18, 20]

# --- AUDIO QUALITY (SMALL HEADER) ---
# Requirement 5: Small caps heading and specific metric rows [cite: 22, 23]
st.markdown('<p class="small-header">AUDIO QUALITY</p>', unsafe_allow_html=True)
q1, q2, q3, q4, q5 = st.columns(5)
q1.metric("DURATION", "190.6s")
q2.metric("SAMPLE RATE", "44 kHz")
q3.metric("SNR", "35.4 dB")
q4.metric("SILENCE", "20.0%")
q5.metric("CLIPPING", "0.000%")

s1, s2, s3, s4, s5, s6 = st.columns(6)
s1.metric("SCORING", "1.000")
s2.metric("WER", "0.304") # [cite: 21]
s3.metric("CER", "0.152")
s4.metric("SEMANTIC", "0.9836") # 
s5.metric("PSDN", "1.000")
s6.metric("QUALITY TIER", "Gold")

# --- TEXT COMPARISON (SMALL TEXT) ---
# Requirement 4: Compact side-by-side Bengali text [cite: 24, 33]
st.markdown('<p class="small-header">TEXT COMPARISON</p>', unsafe_allow_html=True)
t_ref, t_hyp = st.columns(2)
with t_ref:
    st.markdown('<p class="small-header">REFERENCE</p>', unsafe_allow_html=True)
    st.markdown('<div class="small-text">হেই করিম আমি দেশে এর সরছে তুমি কি জানো প্রধানমন্ত্রী আ...</div>', unsafe_allow_html=True)
with t_hyp:
    st.markdown('<p class="small-header">HYPOTHESIS</p>', unsafe_allow_html=True)
    st.markdown('<div class="small-text">হেই করিম তুমি কি জানো প্রতিনিধি দল এর এখা...</div>', unsafe_allow_html=True)

# --- STRUCTURAL QUALITY CHECK ---
st.write("---")
st.header("STRUCTURAL QUALITY CHECK")
# Requirement 3: File inputs for QC
st.file_uploader("Upload .json Transcript", type=["json"])
st.file_uploader("Upload Audio File", type=["wav"])

st.subheader("ISSUES FOUND IN STRUCTURAL QC")
# Displaying issues matching document warnings [cite: 41, 42]
st.warning("Warning: Segment 1: unexpected speaker label 'Speaker A', expected 'speaker a' or 'speaker b'")
st.warning("Warning: Segment 2: unexpected speaker label 'Speaker B', expected 'speaker a' or 'speaker b'")

# --- ACCURACY QUALITY CHECK ---
# Requirement 6: Side-by-side highlighting
st.write("---")
st.header("ACCURACY QUALITY CHECK")
acc_ref, acc_hyp = st.columns(2)

with acc_ref:
    st.subheader("Reference")
    st.markdown('হেই করিম আমি <span class="highlight-red">দেশে</span> এর সরছে তুমি কি জানো প্রধানমন্ত্রী...', unsafe_allow_html=True)

with acc_hyp:
    st.subheader("Hypothesis")
    st.markdown('হেই করিম আমি <span class="highlight-green">জানো</span> এর সরছে তুমি কি জানো প্রধানমন্ত্রী...', unsafe_allow_html=True)

st.subheader("ISSUES FOUND IN ACCURACY QC")
# Requirement 7: Accuracy mismatch logs
st.error("MISMATCH [Segment 1]: Reference 'দেশে' was predicted as 'জানো'.")