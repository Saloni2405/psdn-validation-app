import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Updated CSS: Everything is centered and styled to match your reference image
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* 1. Target the actual Streamlit Upload Box and Center Everything */
    [data-testid="stFileUploader"] section {
        background-color: #1E1F23 !important;
        border: 2px dashed #333 !important;
        border-radius: 12px !important;
        padding: 80px 30px !important; 
        display: flex;
        flex-direction: column;
        align-items: center;      /* Centers horizontally */
        justify-content: center;    /* Centers vertically */
        min-height: 280px;         /* Maintains the large expanded look */
    }

    /* 2. Style the 'Browse files' button to be dark grey with white text */
    [data-testid="stFileUploader"] button {
        background-color: #2D2E35 !important;
        border: 1px solid #444 !important;
        color: white !important;
        border-radius: 8px !important;
        margin-top: 10px; 
    }

    /* 3. Custom Pill styling: Positioned inside the bottom of the box */
    .pill-wrapper {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: -65px; /* Pulls pills into the expanded dashed area */
        position: relative;
        z-index: 1;
        padding-bottom: 20px;
    }
    
    .pill {
        background-color: #2D2E35;
        border: 1px solid #444;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 13px;
        color: #E0E0E0;
    }

    /* 4. Right-aligned Royal Blue Button */
    div.stButton > button:first-child {
        background-color: #4169E1 !important;
        color: white !important;
        border: none !important;
        float: left; /* Kept left as per your latest screenshot reference */
        padding: 8px 24px !important;
        border-radius: 6px !important;
    }

    /* 5. Validation Settings Styles */
    .stExpander { 
        background-color: #1E1F23 !important; 
        border: 1px solid #333 !important; 
    }
    label p { 
        font-weight: bold !important; 
        color: #E0E0E0 !important; 
        font-size: 12px !important; 
    }
    .stCaption { 
        color: #808495 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("NEW VALIDATION RUN")

# --- DATA LOGIC ---
REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']
valid_csv = False

st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# The functional uploader
main_csv = st.file_uploader(
    "Drag & drop your CSV file here", 
    type="csv", 
    label_visibility="visible"
)

# The pills that appear inside the box visually
st.markdown(f"""
    <div class="pill-wrapper">
        {"".join([f'<div class="pill">{col}</div>' for col in REQUIRED_COLUMNS])}
    </div>
    """, unsafe_allow_html=True)

# --- ERROR HANDLING LOGIC ---
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
            st.success("CSV validated successfully.")
    except Exception as e:
        st.error(f"**Parse Errors**\n\n• Could not read CSV file: {str(e)}")
        valid_csv = False

# VALIDATION SETTINGS
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
st.button("Start Validation", disabled=not valid_csv)