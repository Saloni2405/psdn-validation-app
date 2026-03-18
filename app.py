import streamlit as st

st.set_page_config(layout="wide")

# CSS to force the dark theme and handle the "Start Validation" button placement
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Center the main container */
    .main-container {
        max-width: 1000px;
        margin: auto;
    }

    /* Custom Drag & Drop Box based on your SS */
    .upload-box {
        background-color: #1E1F23;
        border: 2px dashed #333;
        border-radius: 12px;
        padding: 60px 20px;
        text-align: center;
        color: #E0E0E0;
        cursor: pointer;
        transition: 0.3s;
    }
    .upload-box:hover { border-color: #4169E1; }
    
    .upload-icon { font-size: 40px; color: #808495; margin-bottom: 15px; }
    .primary-text { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    .secondary-text { color: #808495; font-size: 14px; margin-bottom: 25px; }
    .browse-link { color: #4169E1; text-decoration: underline; cursor: pointer; }

    /* Pill styling strictly from your reference */
    .pill-wrapper {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .pill {
        background-color: #2D2E35;
        border: 1px solid #444;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 13px;
    }

    /* Start Validation Button - Right Aligned Royal Blue */
    div.stButton > button {
        background-color: #4169E1 !important;
        color: white !important;
        border: none !important;
        float: right;
        padding: 8px 24px !important;
    }

    /* Dark Expander Styling for Validation Settings */
    .stExpander {
        background-color: #1E1F23 !important;
        border: 1px solid #333 !important;
        margin-top: 20px;
    }
    label p { font-weight: bold !important; color: #E0E0E0 !important; font-size: 12px !important; }
    .stCaption { color: #808495 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("NEW VALIDATION RUN")

with st.container():
    st.write("### Upload Audio Dataset CSV")
    st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")
    
    # EXACT UI FROM YOUR SCREENSHOT (But Dark)
    st.markdown("""
        <div class="upload-box">
            <div class="upload-icon">📤</div>
            <div class="primary-text">Drag & drop your CSV file</div>
            <div class="secondary-text">or <span class="browse-link">click to browse</span></div>
            <div class="pill-wrapper">
                <div class="pill">audio_id</div>
                <div class="pill">speaker_A_audio</div>
                <div class="pill">speaker_B_audio</div>
                <div class="pill">combined_audio</div>
                <div class="pill">transcription</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Hidden actual uploader to handle the file logic
    uploaded_file = st.file_uploader("Upload", type="csv", label_visibility="collapsed")

# VALIDATION SETTINGS SECTION
with st.expander("⚙️ Validation Settings", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.number_input("MIN DURATION (S)", value=1)
        st.caption("Minimum audio length")
    with col2:
        st.number_input("MAX DURATION (S)", value=600)
        st.caption("Maximum audio length")
    with col3:
        st.number_input("WER THRESHOLD", value=0.15)
        st.caption("Max WER to pass (0-1)")
    with col4:
        st.number_input("CONCURRENCY", value=3)
        st.caption("Parallel rows (1-10)")

st.markdown("<br>", unsafe_allow_html=True)
st.button("Start Validation")