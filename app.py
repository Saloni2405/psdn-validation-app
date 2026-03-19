import streamlit as st
import pandas as pd

# --- DIALOG FOR ROW DETAILS ---
@st.dialog("Row Details")
def show_details(row_data, row_index):
    st.write(f"### {row_data.get('audio_id', f'Row {row_index}')}")
    
    st.markdown("---")
    st.write("**SPEAKER A AUDIO**")
    st.caption(f"🔗 {row_data.get('speaker_A_audio', 'N/A')}")
    
    st.write("**SPEAKER B AUDIO**")
    st.caption(f"🔗 {row_data.get('speaker_B_audio', 'N/A')}")
    
    st.write("**COMBINED AUDIO**")
    st.caption(f"🔗 {row_data.get('combined_audio', 'N/A')}")
    
    st.write("**TRANSCRIPTION JSON**")
    st.code(row_data.get('transcription', '{}'), language='json')
    
    st.markdown("---")
    st.markdown("#### 🎙️ Structural Validation <span style='float:right;' class='badge-fail'>Fail</span>", unsafe_allow_html=True)
    
    # Specific error messages based on your screenshot
    st.error("""
    - Speaker A audio: Invalid WAV header: expected 'RIFF', got 'ID3'
    - Speaker B audio: Invalid WAV header: expected 'RIFF', got 'ID3'
    - Combined audio: Invalid WAV header: expected 'RIFF', got 'ID3'
    - Transcription: Fetch error: Invalid URL
    """)
    
    st.markdown("#### 📈 Accuracy Validation <span style='float:right;' class='badge-skipped'>Skipped</span>", unsafe_allow_html=True)
    st.info("Skipped – structural check failed")

# --- UPDATED STEP 3 LOGIC ---
if st.session_state.step == 3:
    # (Header and Metrics remain the same as previous code)
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.subheader("Validation Report")
        st.write(f"{st.session_state.get('filename', 'File')} — {len(st.session_state.df)} rows processed")
    with h_col2:
        st.button("📥 Download CSV")

    # 1. Dashboard Metrics
    m1, m2, m3, m4 = st.columns(4)
    # ... (metric-card HTML as provided before)

    st.write("### Detailed Results")
    
    # Header for the table
    t_h1, t_h2, t_h3, t_h4 = st.columns([1, 3, 1, 1])
    t_h1.caption("AUDIO ID")
    t_h2.caption("STRUCTURAL")
    t_h3.caption("WER SCORE")
    t_h4.caption("ACCURACY")

    # 2. Detailed Results List with Modal Trigger
    for index, row in st.session_state.df.iterrows():
        with st.container(border=True):
            r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([1, 2, 1, 1, 0.5])
            
            with r_col1:
                st.write(f"**{row.get('audio_id', f'test_{index}')}**")
            
            with r_col2:
                st.markdown('<span class="badge-fail">ⓧ Fail</span>', unsafe_allow_html=True)
                st.caption("Multiple structural errors detected...")
            
            with r_col3:
                st.write("--")
                
            with r_col4:
                st.markdown('<span class="badge-skipped">Skipped</span>', unsafe_allow_html=True)
                
            with r_col5:
                # This button triggers the Modal
                if st.button("ⓘ", key=f"btn_{index}"):
                    show_details(row, index)

    if st.button("← Back to Settings"):
        st.session_state.step = 2
        st.rerun()