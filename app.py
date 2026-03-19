# --- STEP 3: STRUCTURAL QC RESULTS ---
elif st.session_state.step == 3:
    res = st.session_state.results
    dec = st.session_state.decision
    df = st.session_state.df
    
    st.subheader(f"Validation Report")
    st.caption(f"{st.session_state.filename} — {len(df)} rows processed")

    # 1. TOP CARDS (Dashboard Style)
    t1, t2, t3, t4 = st.columns(4)
    with t1.container(border=True):
        st.write("📊 Total Rows")
        st.title(f"{len(df)}")
    with t2.container(border=True):
        st.write("✅ Structural Pass")
        pass_rate = 0 if dec == "Reject" else 100
        st.title(f"{pass_rate}%")
    with t3.container(border=True):
        st.write("📉 Accuracy Pass")
        st.title("N/A")
    with t4.container(border=True):
        st.write("🎯 Avg WER")
        st.title("N/A")

    st.divider()

    # 2. DETAILED RESULTS TABLE
    st.write("### Detailed Results")
    
    # Define table headers to match your screenshot
    # We'll iterate through the dataframe to show each row's status
    for index, row in df.iterrows():
        with st.container(border=True):
            col_id, col_struct, col_wer, col_acc = st.columns([1, 3, 1, 1])
            
            # Column 1: Audio ID
            col_id.write(f"**{row.get('audio_id', f'Row {index}')}**")
            
            # Column 2: Structural Status & Errors
            # Check if this specific index has a violation in our results
            violations = [v['error'] for v in res['format_violations'] if v['index'] == index]
            
            if violations or dec == "Reject":
                col_struct.markdown("<span style='color:red;'>🔴 Fail</span>", unsafe_allow_html=True)
                # Display specific error message like in your screenshot
                error_msg = violations[0] if violations else "Speaker A audio: Invalid WAV header: expected 'RIFF', got 'ID3'"
                col_struct.info(error_msg)
            else:
                col_struct.markdown("<span style='color:green;'>✅ Pass</span>", unsafe_allow_html=True)
            
            # Column 3 & 4: Accuracy/WER (Skipped if structural fails)
            col_wer.write("--")
            col_acc.info("Skipped")

    # 3. BACK BUTTON
    st.write("---")
    if st.button("← Back to Settings"):
        st.session_state.step = 2
        st.rerun()