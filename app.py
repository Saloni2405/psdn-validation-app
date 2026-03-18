# --- STEP 1: UPLOAD ---
if st.session_state.step == 'upload':
    st.write("### Upload Audio Dataset CSV")
    
    # 1. The Uploader Box
    main_csv = st.file_uploader("Upload", type="csv", label_visibility="collapsed")
    
    # 2. Persistent Pills inside the box area
    st.markdown(f"""
        <div class="pill-container">
            {''.join([f'<div class="pill">{c}</div>' for c in REQUIRED_COLUMNS])}
        </div>
    """, unsafe_allow_html=True)

    # 3. Processing & Preview
    if main_csv is not None:
        try:
            df = pd.read_csv(main_csv)
            if all(col in df.columns for col in REQUIRED_COLUMNS):
                st.session_state.df = df
                st.session_state.file_name = main_csv.name
                
                # Header with green checkmark
                st.markdown(f"""
                    <div class="preview-header">
                        <span class="status-icon">✅</span>
                        <span style="font-weight: 500; color: #E0E0E0;">{main_csv.name}</span>
                    </div>
                    <div class="row-info">{len(df)} rows parsed</div>
                """, unsafe_allow_html=True)
                
                # Data Preview
                st.table(df.head(2))
                
                # --- RIGHT ALIGNED BUTTON ---
                # column [4, 1] creates a large spacer on the left
                col_spacer, col_btn = st.columns([4, 1]) 
                with col_btn:
                    if st.button("Continue to Validation →", use_container_width=True):
                        st.session_state.step = 'ready'
                        st.rerun()
            else:
                st.error("CSV is missing required columns.")
        except Exception as e:
            st.error(f"Error parsing CSV: {e}")