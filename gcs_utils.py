from google.cloud import storage

GCS_BUCKET = "BUCKET_NAME"  # Replace with your GCS bucket name
GCS_PREFIX = "PATH/TO/AUDIO/FILES"  # Replace with the prefix path to your audio files in the bucket

# make sure gcloud is set to the correct project and
# that gcloud auth application-default login has been
# run to set up credentials

def get_audio_bytes(parent_dir: str, audio_file: str) -> bytes:
    """Fetch audio bytes from GCS without writing to disk."""
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(f"{GCS_PREFIX}/{parent_dir}/{audio_file}")
    return blob.download_as_bytes()
