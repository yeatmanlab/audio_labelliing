import streamlit as st
import pandas as pd
import os
import argparse

from gcs_utils import get_audio_bytes

parser = argparse.ArgumentParser()
parser.add_argument("--gcs-bucket", default="roar-assessment-recordings-prod")
parser.add_argument("--gcs-prefix", default="ran")
parser.add_argument("--local-path", default=None, help="If set, load audio from local disk instead of GCS")
args = parser.parse_args()

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
    'truncated': False,
    'good_audio': True
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
        'truncated': False,
        'good_audio': True
    }
    
    for key, value in default_values.items():
        st.session_state[key] = value

if csv_file is not None:
    try:
        if st.session_state.data is None:
            st.session_state.data = pd.read_csv(csv_file)
            df = st.session_state.data


        else:
            df = st.session_state.data

        data_cols = ["start_time", "end_time", "use", 
                     "graded", "num_errors","background_noise",
                     "interrupted","inaudible","static","truncated","good_audio"]

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
            assessment_pid = current_row['assessment_pid']
            assessment_uid = current_row['assessment_uid']
            file_path = current_row['file_path']
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

            # Stream audio bytes from GCS
            if args.local_path:
                local_file = os.path.join(args.local_path, file_path)
                with open(local_file, "rb") as f:
                    audio_bytes = f.read()
            else:
                file_dir = "/".join(file_path.split('/')[:-1])
                audio_bytes = get_audio_bytes(file_dir, audio_file, gcs_bucket=args.gcs_bucket, gcs_prefix=args.gcs_prefix)
            st.audio(audio_bytes, format="audio/webm")

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
            good_audio = st.checkbox("Is the audio good enough for hand scoring?", value=True, key=f"good_audio_{widget_key_suffix}")

            # reset inputs if flag is set
            if st.session_state.reset_inputs:
                reset_inputs()
                st.session_state.reset_inputs = False

            col1, col2 = st.columns(2)

            # --- Save and Next ---
            with col1:
                if st.button("✅ Useful Audio for \nModel Training- Save and Next"):
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
                        truncated,
                        good_audio
                    ]
                    df.to_csv(csv_file.name, index=False)
                    handle_save_or_discard()  # Set flag to reset inputs on next run
                    st.rerun()

            # --- Discard and Next ---
            with col2:
                if st.button("🗑️ Discard and Next"):
                    df.loc[df["audio_file"] == audio_file, data_cols] = [
                        start_time,
                        end_time,
                        False,
                        True,
                        num_errors,
                        background_noise_flag,
                        interruption_flag,
                        inaudible_flag,
                        static_flag,
                        truncated,
                        good_audio
                    ]
                    df.to_csv(csv_file.name, index=False)
                    handle_save_or_discard()  # Set flag to reset inputs on next run
                    st.rerun()

        else:
            st.success("🎉 All audio files have been processed!")

    except Exception as e:
        st.error(f"Error loading file: {e}")


