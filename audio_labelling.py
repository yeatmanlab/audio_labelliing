import streamlit as st
import glob
import os
import pandas as pd
import tempfile
import shutil

audio_file_type = "Letter" #or change to Number

# audio_files = glob.glob(f"/Users/aryamant/Desktop/Labelling/CA_Audio/*/*{audio_file_type}*.webm")
audio_files = glob.glob(f"/Users/ethanroy/Documents/Stanford/ROAR-RAN/audio_labelliing/**/RAN_{audio_file_type}*.webm")

# Load or create a CSV to store timestamps
csv_file = f"audio_timestamps_{audio_file_type}.csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file, index_col=0)
else:
    df = pd.DataFrame(columns=["start_time", "end_time", "transcript"])

# Progress tracking
total_files = len(audio_files)
completed_files = len(df)
remaining_files = total_files - completed_files
progress_percent = int((completed_files / total_files) * 100) if total_files else 0

# Sidebar display
st.sidebar.title("Progress Tracker")
st.sidebar.markdown(f"**Completed:** {completed_files} / {total_files}")
st.sidebar.progress(progress_percent / 100)

# Filter out already processed files
unprocessed_files = [f for f in audio_files if os.path.basename(f) not in df.index]

if unprocessed_files:
    audio_file = unprocessed_files[0]
    filename = os.path.basename(audio_file)

    st.title("Audio Timestamp Labeling")

    st.markdown("""
    ### Instructions for RAs:
    - Listen to the full audio clip using the player below.
    - If the participant **spoke clearly**:
        1. Identify the time **they started and stopped speaking**.
        2. Enter those times (in seconds) into the fields below.
        3. Enter what they said in the third field, with each word 
                separated by a space.
        4. Click **✅ Save and Next** to move on.
    - If the audio is **inaudible**, **empty**, or **not usable**, click **🗑️ Discard and Next** instead.
    """)

    st.write(f"Now labeling: `{filename}`")

    # Copy file to a temp directory to serve via Streamlit
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_audio:
        shutil.copy(audio_file, tmp_audio.name)
        audio_path = tmp_audio.name

    # Display audio player
    st.audio(audio_path, format="audio/webm")

    start_time = st.number_input("Start Time (in seconds)", min_value=0.0, step=0.1, value=0.0)
    end_time = st.number_input("End Time (in seconds)", min_value=0.0, step=0.1, value=0.0)
    transcript = st.text_input("Audio Transcript")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Save and Next"):
            df.loc[filename] = [start_time, end_time, transcript]
            df.to_csv(csv_file)
            st.rerun()

    with col2:
        if st.button("🗑️ Discard and Next"):
            df.loc[filename] = [0, 0, ""]
            df.to_csv(csv_file)
            st.rerun()
else:
    st.success("🎉 All audio files have been processed!")
