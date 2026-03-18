import streamlit as st

# Page configuration
st.set_page_config(page_title="Validation PSDN App", layout="wide")

# Updated CSS for a clean, centered, non-overlapping layout
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }

    /* Target the uploader box */
    [data-testid="stFileUploader"] {
        background-color: #1E1F23 !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        padding: 50px 20px !important;
        text-align: center;
    }

    /* Center all internal elements vertically */
    [data-testid="stFileUploader"] section {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 15px;
    }

    /* Style for the nested pills at the bottom of the box */
    .pill-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 20px;
        width: 100%;
    }

    .column-pill {
        background-color: #2D2E35;
        color: #E0E0E0;
        padding: 6px 12px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 12px;
        border: 1px solid #444;
        white-space: nowrap;
    }

    /* Styling for the help text in Validation Settings */
    .stCaption {
        color: #808495 !important;
        font-size: 12px !important;
        margin-top: -10px;
    }

    /* Start Validation Button */
    div.stButton > button:first-child {
        background-color: #4169E1;
        color: white;
        border: None;
        float: right;
        padding: 10px 25px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("NEW VALIDATION RUN")

st.write("### Upload Audio Dataset CSV")
st.write("Select folder containing a CSV with Google Drive links to WAV files and a transcription JSON file per row.")

# The Uploader Block
# We use a container to wrap the uploader and our custom pills
with st.container():
    # Primary Uploader
    main_csv = st.file_uploader(
        "**Drag & drop your CSV file** or click to browse",
        type=["csv"],
        label_visibility="collapsed"
    )
    
    # Custom Pills placed logically below the browse area
    st.markdown("""
        <div class="pill-container">
            <span class="column-pill">audio_id</span>
            <span class="column-pill">speaker_A_audio</span>
            <span class="column-pill">speaker_B_audio</span>
            <span class="column-pill">combined_audio</span>
            <span class="column-pill">transcription</span>
        </div>
        """, unsafe_allow_html=True)

# Validation Settings
with st.expander("⚙️ Validation Settings", expanded=True):
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        st.number_input("MIN DURATION (S)", value=1)
        st.caption("Minimum audio length")
    with v_col2:
        st.number_input("MAX DURATION (S)", value=600)
        st.caption("Maximum audio length")
    with v_col3:
        st.number_input("WER THRESHOLD", value=0.15)
        st.caption("Max WER to pass (0-1)")
    with v_col4:
        st.number_input("CONCURRENCY", value=3)
        st.caption("Parallel rows (1-10)")

# Footer Button
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col = st.columns([5, 1])
with btn_col:
    st.button("Start Validation", disabled=not main_csv)