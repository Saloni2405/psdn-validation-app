import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# CSS to expand the block and ensure functional clicks work
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* The Large Visual Upload Box from your screenshot */
    .upload-box {
        background-color: #1E1F23;
        border: 2px dashed #333;
        border-radius: 12px;
        padding: 80px 20px; /* Increased padding to expand the block */
        text-align: center;
        color: #E0E0E0;
        position: relative;
        transition: 0.3s;
    }
    .upload-box:hover { border-color: #4169E1; }
    
    .upload-icon { font-size: 45px; margin-bottom: 20px; }
    .primary-text { font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .secondary-text { color: #808495; font-size: 15px; margin-bottom: 30px; }
    .browse-link { color: #4169E1; text-decoration: underline; }

    /* Pill styling for required columns */
    .pill-wrapper {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
    }
    .pill {
        background-color: #2D2E35;
        border: 1px solid #444;
        padding: 6px 15px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 13px;
        color: #E0E0E0;
    }

    /* POSITIONING THE REAL UPLOADER TO FILL THE ENTIRE LARGE BOX */
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
    
    /* Ensure the internal Streamlit elements don't block the click */
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
        padding: 10px 30px !important;
        border-radius: 6px !important;
    }

    /* Expander Styling */
    .stExpander {
        background-color: #1E1F23 !important;
        border: 1px solid #333 !important;
        margin-top: 30px;
    }
    label p { font-weight: bold !important; color: #E0E0E0 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("NEW VALIDATION RUN")

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']
valid_csv = False

# --- UPLOAD SECTION ---
with st.container():
    st.write("### Upload Audio Dataset CSV")
    st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")
    
    # Large expanded visual block
    st.markdown(f"""
        <div class="upload-box">
            <div class="upload-icon">📤</div>
            <div class="primary-text">Drag & drop your CSV file</div>
            <div class="secondary-text">or <span class="browse-link">click to browse</span></div>
            <div class="pill-wrapper">
                {"".join([f'<div class="pill">{col}</div>' for col in REQUIRED_COLUMNS])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Real functional uploader hidden but filling the expanded box
    main_csv = st.file_uploader("Upload", type="csv", label_visibility="collapsed")

# --- ERROR HANDLING ---
if main_csv is not None:
    try:
        df = pd.read_csv(main_csv)
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_cols:
            st.markdown("<br>", unsafe_allow_html=True)
            st.error(f"**Parse Errors**\n\n• Missing required columns: {', '.join(missing_cols)}")
            valid_csv = False
        else:
            valid_csv = True
            st.success(f"File '{main_csv.name}' validated successfully!")
    except Exception as e:
        st.error(f"**Parse Errors**\n\n• Could not read CSV file: {str(e)}")
        valid_csv = False

# --- VALIDATION SETTINGS ---
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
if st.button("Start Validation", disabled=not valid_csv):
    st.write("Validation process started...")