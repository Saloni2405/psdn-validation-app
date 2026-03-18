import streamlit as st
import pandas as pd
import json
import librosa
import os

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .small-header { font-size: 14px !important; font-weight: bold; text-transform: uppercase; margin-top: 10px; }
    .small-text { font-size: 12px !important; }
    .highlight-red { background-color: #ffcccc; color: #cc0000; padding: 2px; border-radius: 3px; font-weight: bold; }
    .highlight-green { background-color: #ccffcc; color: #006600; padding: 2px; border-radius: 3px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & INPUT ---
st.title("NEW VALIDATION RUN") [cite: 1]
col_input, col_btn = st.columns([4, 1])
with col_input:
    # Detailed placeholder instruction
    st.text_input("Input Source", placeholder="select a folder containing .csv file , or a parent folder with single_speaker/ and multi_speaker/ subfolders") [cite: 2, 3]
with col_btn:
    st.write("##") 
    if st.button("Start Validation", type="primary"): [cite: 5]
        st.toast("Validation Pipeline Started")

# --- SUMMARY METRICS ---
st.write("---")
m1, m2, m3 = st.columns(3)
m1.metric("TOTAL", "229") [cite: 9]
m2.metric("SUCCEEDED", "226", "↑ 100%") [cite: 11]
m3.metric("FAILED", "0") [cite: 13]
st.caption("items were not processed (pipeline stopped before completion!)") [cite: 12]

# --- PROGRESS ---
st.subheader("PROGRESS") [cite: 17]
st.progress(1.0) [cite: 18]
st.write("100% ITEMS: 225") [cite: 19, 20]

# --- AUDIO QUALITY (SMALL HEADER) ---
st.markdown('<p class="small-header">AUDIO QUALITY</p>', unsafe_allow_html=True) [cite: 22]
q_row1 = st.columns(5)
q_row1[0].metric("DURATION", "190.6s") [cite: 23]
q_row1[1].metric("SAMPLE RATE", "44 kHz") [cite: 23]
q_row1[2].metric("SNR", "35.4 dB") [cite: 23]
q_row1[3].metric("SILENCE", "20.0%") [cite: 23]
q_row1[4].metric("CLIPPING", "0.000%") [cite: 23]

q_row2 = st.columns(6)
q_row2[0].metric("SCORING", "1.000") [cite: 23]
q_row2[1].metric("WER", "0.304") [cite: 21]
q_row2[2].metric("CER", "0.152")
q_row2[3].metric("SEMANTIC", "0.9836") [cite: 23]
q_row2[4].metric("PSDN", "1.000")
q_row2[5].metric("QUALITY TIER", "Gold") [cite: 23]

# --- TEXT COMPARISON ---
st.markdown('<p class="small-header">TEXT COMPARISON</p>', unsafe_allow_html=True) [cite: 24]
t_ref, t_hyp = st.columns(2)
with t_ref:
    st.markdown('<p class="small-text"><b>REFERENCE</b></p>', unsafe_allow_html=True)
    st.caption("হেই করিম আমি দেশে এর সরছে তুমি কি জানো প্রধানমন্ত্রী আ...") [cite: 26]
with t_hyp:
    st.markdown('<p class="small-text"><b>HYPOTHESIS</b></p>', unsafe_allow_html=True)
    st.caption("হেই করিম তুমি কি জানো প্রতিনিধি দল এর এখা...") [cite: 34]

# --- QUALITY CHECKS ---
st.write("---")
st.header("STRUCTURAL QUALITY CHECK")
st.file_uploader("Upload Transcript (.json)", type=["json"])
st.file_uploader("Upload Audio (.wav)", type=["wav"])
st.subheader("ISSUES FOUND IN STRUCTURAL QC") [cite: 40]
st.warning("Warning: Segment 1: unexpected speaker label 'Speaker A', expected 'speaker a' or 'speaker b'") [cite: 41]

st.write("---")
st.header("ACCURACY QUALITY CHECK")
acc_l, acc_r = st.columns(2)
with acc_l:
    st.subheader("Reference")
    st.markdown('হেই করিম আমি <span class="highlight-red">দেশে</span> এর সরছে...', unsafe_allow_html=True)
with acc_r:
    st.subheader("Hypothesis")
    st.markdown('হেই করিম আমি <span class="highlight-green">জানো</span> এর সরছে...', unsafe_allow_html=True)

st.subheader("ISSUES FOUND IN ACCURACY QC")
st.error("MISMATCH [Segment 1]: Reference 'দেশে' vs Predicted 'জানো'")