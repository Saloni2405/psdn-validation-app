import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# CSS for Dark Theme, Visual Upload Box, and Functional Overlap
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Center the main container */
    .main-container {
        max-width: 1000px;
        margin: auto;
    }

    /* The Visual UI Box */
    .upload-box {
        background-color: #1E1F23;
        border: 2px dashed #333;
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        color: #E0E0E0;
        position: relative;
    }
    
    .upload-icon { font-size: 30px; margin-bottom: 10px; }
    .primary-text { font-size: 18px; font-weight: bold; }
    .secondary-text { color: #808495; font-size: 14px; margin-bottom: 20px; }
    .browse-link { color: #4169E1; text-decoration: underline; }

    /* Custom 'Browse files' button look */
    .fake-browse-btn {
        background-color: #2D2E35;
        border: 1px solid #444;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 14px;
        display: inline-block;
        margin-top: 10px;
    }

    .pill-wrapper {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 20px;
    }
    .pill {
        background-color: #2D2E35;
        border: 1px solid #444;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
    }

    /* CRITICAL FIX: Make the real uploader invisible but cover the WHOLE box */
    [data-testid="stFileUploader"] {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        z-index: 10;
        cursor: pointer;
    }
    
    /* Ensure the wrapper doesn't block the invisible uploader */
    [data-testid="stFileUploader"] section {
        height: 100%;
        padding: 0;
    }

    /* Start Validation Button - Royal Blue & Right Aligned */
    div.stButton > button {
        background-color: #4169E1 !important;
        color: white !important;
        border: none !important;
        float: right;
        padding: 8px 24px !important;
        border-radius: 6px !important;
    }

    /* Error box styling */
    .stAlert {
        background-color: rgba(255, 75, 75, 0.1) !important;
        border: 1px solid #ff4b4b !important;
        color: #ff4b4b !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("NEW VALIDATION RUN")

REQUIRED_COLUMNS = ["audio_id", "speaker_A_audio", "speaker_B_audio", "combined_audio", "transcription"]
valid_file = False

# --- UPLOAD SECTION ---
st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# The Box Container
with st.container():
    # 1. Visual Layer
    st.markdown(f"""
        <div class="upload-box">
            <div class="upload-icon">📥</div>
            <div class="primary-text">Drag & drop your CSV file</div>
            <div class="secondary-text">or <span class="browse-link">click to browse</span></div>
            <div class="fake-browse-btn">Browse files</div>
            <div class="pill-wrapper">
                {"".join([f'<div class="pill">{col}</div>' for col in REQUIRED_COLUMNS])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Hidden Functional Layer (now truly overlapping the box)
    uploaded_file = st.file_uploader("", type="csv", label_visibility="collapsed")

# --- ERROR HANDLING ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
        if missing:
            st.markdown("<br>", unsafe_allow_html=True)
            st.error(f"**Parse Errors**\n\n• Missing required columns: {', '.join(missing)}")
        else:
            valid_file = True
            st.success(f"File '{uploaded_file.name}' loaded successfully!")
    except Exception as e:
        st.error(f"**Parse Errors**\n\n• Could not read CSV file: {e}")

# --- SETTINGS SECTION ---
with st.expander("⚙️ Validation Settings", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.number_input("MIN DURATION (S)", value=1, step=1)
        st.caption("Minimum audio length")
    with col2:
        st.number_input("MAX DURATION (S)", value=600, step=1)
        st.caption("Maximum audio length")
    with col3:
        st.number_input("WER THRESHOLD", value=0.15, step=0.01, format="%.2f")
        st.caption("Max WER to pass (0-1)")
    with col4:
        st.number_input("CONCURRENCY", value=3, step=1)
        st.caption("Parallel rows (1-10)")

st.markdown("<br>", unsafe_allow_html=True)
st.button("Start Validation", disabled=not valid_file)