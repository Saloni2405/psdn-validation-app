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

# --- HEADER & INPUT ---
st.title("NEW VALIDATION RUN")
col_input, col_btn = st.columns([4, 1])
with col_input:
    st.text_input("Input Source", 
                 placeholder="select a folder containing .csv file , or a parent folder with single_speaker/ and multi_speaker/ subfolders")
with col_btn:
    st.write("##") 
    if st.button("Start Validation", type="primary"):
        st.toast("Validation Pipeline Started")

# --- SUMMARY METRICS ---
st.write("---")
m1, m2, m3 = st.columns(3)
m1.metric("TOTAL", "229")
m2.metric("SUCCEEDED", "226", "↑ 100%")
m3.metric("FAILED", "0")
st.caption("items were not processed (pipeline stopped before completion!)")

# --- PROGRESS ---
st.subheader("PROGRESS")
st.progress(1.0) 
st.write("100% ITEMS: 225")

# --- AUDIO QUALITY ---
st.markdown('<p class="small-header">AUDIO QUALITY</p>', unsafe_allow_html=True)
q1, q2, q3, q4, q5 = st.columns(5)
q1.metric("DURATION", "190.6s")
q2.metric("SAMPLE RATE", "44 kHz")
q3.metric("SNR", "35.4 dB")
q4.metric("SILENCE", "20.0%")
q5.metric("CLIPPING", "0.000%")

s1, s2, s3, s4, s5, s6 = st.columns(6)
s1.metric("SCORING", "1.000")
s2.metric("WER", "0.304")
s3.metric("CER", "0.152")
s4.metric("SEMANTIC", "0.9836")
s5.metric("PSDN", "1.000")
s6.metric("QUALITY TIER", "Gold")

# --- TEXT COMPARISON ---
st.markdown('<p class="small-header">TEXT COMPARISON</p>', unsafe_allow_html=True)
t_ref, t_hyp = st.columns(2)
with t_ref:
    st.markdown('<p class="small-text"><b>REFERENCE</b></p>', unsafe_allow_html=True)
    st.caption("হেই করিম আমি দেশে এর সরছে তুমি কি জানো প্রধানমন্ত্রী আ...")
with t_hyp:
    st.markdown('<p class="small-text"><b>HYPOTHESIS</b></p>', unsafe_allow_html=True)
    st.caption("হেই করিম তুমি কি জানো প্রতিনিধি দল এর এখা...")

# --- QUALITY CHECKS ---
st.write("---")
st.header("STRUCTURAL QUALITY CHECK")
st.file_uploader("Upload .json", type=["json"])
st.file_uploader("Upload .wav", type=["wav"])
st.subheader("ISSUES FOUND IN STRUCTURAL QC")
st.warning("Warning: Segment 1: unexpected speaker label 'Speaker A', expected 'speaker a' or 'speaker b'")

st.write("---")
st.header("ACCURACY QUALITY CHECK")
acc_col_l, acc_col_r = st.columns(2)
with acc_col_l:
    st.subheader("Reference")
    st.markdown('হেই করিম আমি <span class="highlight-red">দেশে</span> এর সরছে...', unsafe_allow_html=True)
with acc_col_r:
    st.subheader("Hypothesis")
    st.markdown('হেই করিম আমি <span class="highlight-green">জানো</span> এর সরছে...', unsafe_allow_html=True)

st.subheader("ISSUES FOUND IN ACCURACY QC")
st.error("MISMATCH [Segment 1]: Reference 'দেশে' vs Predicted 'জানো'")