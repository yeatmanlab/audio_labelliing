# 🎧 Audio Timestamp Labeling Tool

This Streamlit app allows research assistants to label when a participant starts and stops speaking in recorded audio clips, or to discard unusable ones.

---

## 📁 Setup Instructions

### 1. **Install Google Cloud CLI**

* Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
Note: You will need to request to the `som-nero-phi-jyeatman-webcam` and/or the `gse-roar-assessment` cloud project and set up application default credentials. You can do that by running:

```bash
gcloud auth application-default login \
 --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/drive"
 ```
* If you do not have access to the cloud project, you can also
download the older data (pre-March 2026) from the Google Drive using a Stanford-affiliated Google account. You can download newer data from the ROAR-Assessment Google Cloud Project. 
* Place the folders in the **`audio_data`** directory, which should be in the same directory as this `README.md` file and the `audio_labelling.py` script.
* Your folder structure should look like this:

```
/Labelling/
├── README.md
├── audio_labelling.py
├── audio_data/
    ├── pid_001/
    └── pid_002/
```

### 2. **Install Requirements**

Create a virtual environment (optional but recommended), then install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. **Launch the Streamlit App**

From the same directory, run:

```bash
streamlit run audio_labelling.py
```
Note: if you have multiple GCP projects configured on your local machine, make sure that the correct project is activated when you run the `streamlit` command. To change the active GCP project, run: 

```bash
gcloud config set project <PROJECT_ID>
```
If you need to access data from a different GCP project/bucket, you can pass those in as arguments to the streamlit command:

```bash

streamlit run audio_labelling.py -- --gcs-bucket YOUR_BUCKET_NAME --gcs-prefix FIRST_DIRECTORY_IN_DATA_PATH

```

If you are scoring data saved on your local machine, you can run:

```bash

streamlit run audio_labelling.py -- --local-path" PATH_TO_LOCAL_DATA

```

### 4. **Scoring within the App**

Once the app is launched, you will need to upload a `.csv` file so it knows which audio files to present for scoring. This .csv file needs at minimum three columns:

- `audio_file` - the name of the audio file to score
- `file_path` - the path (either on GCP or your local machine) to the file (this path should also include the file name)
- `groundTruth` - the ground truth RAN stimuli presented to the participant 

Once you launch the app, you can drag and drop the csv file into the app. This will automatically download the audio data (if you don't have it already) and then launch the app. 

By distributing the audio files across multiple `.csv` files, you can divide the work across multiple people—each working on a different dataset.

---

## 🧐 How to Use the App

* You'll be presented with one audio file at a time.
* Listen to the full clip using the audio player.
* If the participant **spoke clearly**:

  * Enter the **start time** and **end time** in seconds.
  * Click ✅ **Save and Next** to save and move on.
* Use the checkboxes to indicate whether in the recording:
  * There is excessive background noise
  * The participant was interrupted
  * The clip is inaudible
* If the clip is **inaudible, empty, or unclear**, click 🗑️ **Discard and Next** instead.

---

## ✅ Output

* Your labels are saved automatically to the same CSV file you uploaded when launching the app. 

This file stores the start and end times (or \[0, 0] if discarded) for each processed audio clip.

---

Send these CSV's back when complete!
