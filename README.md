# 🎧 Audio Timestamp Labeling Tool

This Streamlit app allows research assistants to label when a participant starts and stops speaking in recorded audio clips, or to discard unusable ones.

---

## 📁 Setup Instructions

### 1. **Install Google Cloud CLI**

* Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
Note: You will need to request to the `som-nero-phi-jyeatman-webcam` cloud project and set up application default credentials. You can do that by running:

```bash
gcloud auth application-default login \
 --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/drive"
 ```
* If you do not have access to the cloud project, you can also
download the data from the Google Drive using a Stanford-affiliated Google account.
* Place the folders in the **`audio_data`** directory, which should be in the same directory as this `README.md` file and the `audio_labelling.py` script.
* Your folder structure should look like this:

```
/Labelling/
├── README.md
├── audio_labelling.py
├── audio_data/
    ├── haGCTJT6sYUoVBtuftbldUpKtE82_efschl-hwsch-39691ace/
    └── quaGipSF2vZx7HFKMMQP2Zr3aH62_efschl-hwsch-14e02ac2/
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

### 4. **Choose Your Task Type (Letters or Numbers)**

You will first need to make sure you have a `train_letters.csv` or `train_numbers.csv`. Once you launch the app, you can drag and drop the csv file into the app. This will automatically download the audio data (if you don't have it already) and then launch the app. 

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

* Your labels are saved automatically to a CSV file named:

```
audio_timestamps_{task}.csv
```

This file stores the start and end times (or \[0, 0] if discarded) for each processed audio clip.

---

Send these CSV's back when complete!
