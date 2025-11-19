import streamlit as st
import pandas as pd
import os
import tempfile
import shutil

from download_utils import *
from glob import glob

# this should be chosen by the user
csv_file = st.file_uploader("Choose a CSV file", type=["csv"])

# Track whether file is loaded
if "data" not in st.session_state:
    st.session_state.data = None

# Initialize reset flag if not present
if "reset_inputs" not in st.session_state:
    st.session_state.reset_inputs = False
    
# Initialize session state for inputs if not already set
default_values = {
    'start_time': 0.0,
    'end_time': 0.0,
    'num_errors': 0,
    'background_noise': False,
    'interruption': False,
    'inaudible': False,
    'static': False,
    'truncated': False
}
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

def handle_save_or_discard():
    # Set flag to reset inputs on next rerun
    st.session_state.reset_inputs = True

def reset_inputs():
    default_values = {
        'start_time': 0.0,
        'end_time': 0.0,
        'num_errors': 0,
        'background_noise': False,
        'interruption': False,
        'inaudible': False,
        'static': False,
        'truncated': False
    }
    
    for key, value in default_values.items():
        st.session_state[key] = value

if csv_file is not None:
    try:
        if st.session_state.data is None:
            st.session_state.data = pd.read_csv(csv_file)
            df = st.session_state.data
            # download audio data here download_audio
            # download the audio data from google drive
            drive_service = set_up_gdrive()
            # Show a temporary "Downloading data" message
            with st.status("Downloading data from Google Drive...", expanded=False) as status:
                df.apply(lambda row: download_ran_file(row, drive_service), axis=1)
                status.update(label="Download complete!", state="complete", expanded=False)


        else:
            df = st.session_state.data

        data_cols = ["start_time", "end_time", "use", 
                     "graded", "num_errors","background_noise",
                     "interrupted","inaudible","static","truncated"]

        for col in data_cols:
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
                shutil.copy(f"./audio_data/{parent_dir}/{audio_file}", tmp_audio.name)
                audio_path = tmp_audio.name

            # Display audio player
            st.audio(audio_path, format="audio/webm")

            # Show ground truth text
            st.markdown(f"**Ground Truth:** {ground_truth}")

            # generate new identifiers for each input
            widget_key_suffix = current_row.name if hasattr(current_row, 'name') else audio_file

            # Inputs - default values will be used for new keys
            start_time = st.number_input("Start Time (in seconds)", min_value=0.0, step=0.1, key=f"start_time_{widget_key_suffix}")
            end_time = st.number_input("End Time (in seconds)", min_value=0.0, step=0.1, key=f"end_time_{widget_key_suffix}")
            num_errors = st.number_input("Number of Errors", min_value=0, step=1, key=f"num_errors_{widget_key_suffix}")

            # Recording Reliability Flags
            background_noise_flag = st.checkbox("Background Noise?", key=f"background_noise_{widget_key_suffix}")
            interruption_flag = st.checkbox("Interruption?", key=f"interruption_{widget_key_suffix}")
            inaudible_flag = st.checkbox("Recording Inaudible?", key=f"inaudible_{widget_key_suffix}")
            static_flag = st.checkbox("Static in Recording?", key=f"static_{widget_key_suffix}")
            truncated = st.checkbox("Fewer Letters than Ground Truth?", key=f"truncated_{widget_key_suffix}")

            # reset inputs if flag is set
            if st.session_state.reset_inputs:
                reset_inputs()
                st.session_state.reset_inputs = False

            col1, col2 = st.columns(2)

            # --- Save and Next ---
            with col1:
                if st.button("✅ Save and Next"):
                    df.loc[df["audio_file"] == audio_file, data_cols] = [
                        start_time,
                        end_time,
                        True,
                        True,
                        num_errors,
                        background_noise_flag,
                        interruption_flag,
                        inaudible_flag,
                        static_flag,
                        truncated
                    ]
                    df.to_csv(csv_file.name, index=False)
                    handle_save_or_discard()  # Set flag to reset inputs on next run
                    st.rerun()

            # --- Discard and Next ---
            with col2:
                if st.button("🗑️ Discard and Next"):
                    df.loc[df["audio_file"] == audio_file, data_cols] = [
                        0,
                        0,
                        False,
                        True,
                        0,
                        background_noise_flag,
                        interruption_flag,
                        inaudible_flag,
                        static_flag,
                        truncated
                    ]
                    df.to_csv(csv_file.name, index=False)
                    handle_save_or_discard()  # Set flag to reset inputs on next run
                    st.rerun()

        else:

            # give user option to remove audio files from local machine
            if 'delete_message' not in st.session_state:
                st.warning("Would you like to delete the uploaded files?")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, delete files"):
                        
                        audio_dirs = glob(f"./audio_data/*")
                        print(audio_dirs)
                        
                        for dir in audio_dirs or []:
                            if os.path.isdir(dir):
                                shutil.rmtree(dir)
                        st.success("Files deleted successfully.")
                        st.session_state.delete_message = True
                        st.rerun()

                with col2:
                    if st.button("❌ No, keep files"):
                        st.info("Files kept on the server.")
                        st.session_state.delete_message = True
                        st.rerun()


            st.success("🎉 All audio files have been processed!")
            # remove downloaded data from local machine when finished

    except Exception as e:
        st.error(f"Error loading file: {e}")


