import streamlit as st
import pandas as pd
import os
import tempfile
import shutil

csv_file = "TrainingLetter_test.csv"

# --- Load and prepare data ---
df = pd.read_csv(csv_file)

# Ensure required columns exist
for col in ["use", "start_time", "end_time", "graded", "num_errors"]:
    if col not in df.columns:
        df[col] = None

# Identify ungraded rows
ungraded_rows = df[df["graded"].isna() | (df["graded"] == False)]

# Sidebar progress
total_files = len(df)
completed_files = len(df[df["graded"] == True])
progress_percent = int((completed_files / total_files) * 100) if total_files else 0

st.sidebar.title("Progress Tracker")
st.sidebar.markdown(f"**Completed:** {completed_files} / {total_files}")
st.sidebar.progress(progress_percent / 100)

# --- Main UI ---
if not ungraded_rows.empty:
    current_row = ungraded_rows.iloc[0]
    parent_dir = current_row['parentDir']
    audio_file = current_row["audio_file"]
    ground_truth = current_row["groundTruth"]
    filename = os.path.basename(audio_file)

    st.title("Audio Timestamp Labeling")
    st.write(f"Now labeling: `{filename}`")

    st.markdown("""
    ### Instructions for RAs:
    - Listen to the full audio clip using the player below.
    - If the participant **spoke clearly**:
        1. Identify when they **start and stop speaking**.
        2. Enter those times (in seconds) below.
        3. Enter the **number of pronunciation errors** if any.
        4. Click **✅ Save and Next**.
    - If the audio is **inaudible** or **unusable**, click **🗑️ Discard and Next** instead.
    """)

    # Temporary copy for Streamlit player
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_audio:
        shutil.copy(f"./{parent_dir}/{audio_file}", tmp_audio.name)
        audio_path = tmp_audio.name

    # Display audio player
    st.audio(audio_path, format="audio/webm")

    # Show ground truth text
    st.markdown(f"**Ground Truth:** {ground_truth}")

    # Inputs
    start_time = st.number_input("Start Time (in seconds)", min_value=0.0, step=0.1)
    end_time = st.number_input("End Time (in seconds)", min_value=0.0, step=0.1)
    num_errors = st.number_input("Number of Errors", min_value=0, step=1)

    col1, col2 = st.columns(2)

    # --- Save and Next ---
    with col1:
        if st.button("✅ Save and Next"):
            df.loc[df["audio_file"] == audio_file, ["start_time", "end_time", "use", "graded", "num_errors"]] = [
                start_time,
                end_time,
                True,
                True,
                num_errors,
            ]
            df.to_csv(csv_file, index=False)
            st.rerun()

    # --- Discard and Next ---
    with col2:
        if st.button("🗑️ Discard and Next"):
            df.loc[df["audio_file"] == audio_file, ["start_time", "end_time", "use", "graded", "num_errors"]] = [
                0,
                0,
                True,
                True,
                0,
            ]
            df.to_csv(csv_file, index=False)
            st.rerun()

else:
    st.success("🎉 All audio files have been processed!")
