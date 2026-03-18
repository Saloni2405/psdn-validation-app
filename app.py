import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Updated CSS for a cleaner, centered layout
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* 1. Large, Centered Upload Box */
    [data-testid="stFileUploader"] section {
        background-color: #1E1F23 !important;
        border: 2px dashed #333 !important;
        border-radius: 12px !important;
        padding: 60px 20px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 280px !important;
    }

    /* Hide default file info to avoid clutter */
    [data-testid="stFileUploaderFileName"], [data-testid="stFileUploaderFileData"] { display: none; }

    /* 2. Style the 'Browse files' button */
    [data-testid="stFileUploader"] button {
        background-color: #2D2E35 !important;
        border: 1px solid #444 !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* 3. Pills positioned inside the box */
    .pill-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: -85px; /* Pulls pills into the dashed box */
        padding-bottom: 50px;
        position: relative;
        z-index: 10;
    }
    .pill {
        background-color: #2D2E35;
        border: 1px solid #444;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        color: #808495;
    }

    /* 4. Success Preview Styling (Matching Screenshot) */
    .preview-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 30px;
    }
    .status-icon { color: #4CAF50; font-size: 1.2rem; }
    .row-info { color: #808495; font-size: 0.85rem; margin-left: 32px; margin-bottom: 15px; }
    .showing-text { color: #808495; font-size: 0.85rem; float: right; }

    /* 5. Start Validation Button */
    div.stButton > button:first-child {
        background-color: #4169E1 !important;
        color: white !important;
        border: none !important;
        padding: 10px 30px !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("NEW VALIDATION RUN")

REQUIRED_COLUMNS = ['audio_id', 'speaker_A_audio', 'speaker_B_audio', 'combined_audio', 'transcription']
valid_csv = False

st.write("### Upload Audio Dataset CSV")
st.caption("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# --- UPLOAD AREA WRAPPED IN CONTAINER ---
with st.container():
    main_csv = st.file_uploader("Drag & drop your CSV file here", type="csv", label_visibility="collapsed")
    
    # Column Pills (Visually nested in the box)
    st.markdown(f"""
        <div class="pill-container">
            {''.join([f'<div class="pill">{col}</div>' for col in REQUIRED_COLUMNS])}
        </div>
    """, unsafe_allow_html=True)

# --- CSV PROCESSING & PREVIEW ---
if main_csv is not None:
    try:
        df = pd.read_csv(main_csv)
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
        if not missing_cols:
            valid_csv = True
            
            # This matches your 9:58 PM screenshot header exactly
            st.markdown(f"""
                <div class="preview-header">
                    <span class="status-icon">✅</span>
                    <span style="font-weight: 500; color: #E0E0E0;">{main_csv.name}</span>
                    <span style="flex-grow: 1;"></span>
                    <span class="showing-text">👁️ Showing first 2 rows</span>
                </div>
                <div class="row-info">{len(df)} rows parsed</div>
            """, unsafe_allow_html=True)
            
            # Display the data table
            st.table(df.head(2))
            
        else:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
            
    except Exception as e:
        st.error(f"Error reading CSV: {e}")

# --- SETTINGS ---
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
if st.button("Start Validation", disabled=not valid_csv):
    st.info("Initiating validation pipeline...")