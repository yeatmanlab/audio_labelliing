from google.cloud import storage

GCS_BUCKET = "roav-ran-analysis"
GCS_PREFIX = "data/raw/audio_files"

# make sure gcloud is set to the correct project and
# that gcloud auth application-default login has been
# run to set up credentials

def get_audio_bytes(parent_dir: str, audio_file: str, gcs_bucket: str = "roav-ran-analysis", gcs_prefix: str = "data/raw/audio_files") -> bytes:
    """Fetch audio bytes from GCS without writing to disk."""
    client = storage.Client()
    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(f"{gcs_prefix}/{parent_dir}/{audio_file}")
    return blob.download_as_bytes()
