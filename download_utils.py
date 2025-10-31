import argparse
import os
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from pathlib import Path


def set_up_gdrive(service_account_file):

    # Load service account credentials
    SERVICE_ACCOUNT_FILE = service_account_file
    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Initialize Google Drive API
    drive_service = build('drive', 'v3', credentials=creds)

    return drive_service


def get_folder_id(folder_name, drive_service, parent_folder_id=None):
    """Search for a folder by name in Google Drive and return its ID."""
    
    # Base query for searching folder by name
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    
    # If a parent folder ID is provided, search within it
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    # Execute query
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])

    # Return first folder ID found, or None if not found
    return folders[0]['id'] if folders else None

# Function to search for the file in a specific folder
def search_file(filename, parent_folder_id, drive_service):
    query = f"name = '{filename}' and '{parent_folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    return files[0]['id'] if files else None

# Function to download a file
def download_file(file_id, drive_service, destination):
    """Download a file from Google Drive and ensure the destination directory exists."""
    
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    print(destination)

    request = drive_service.files().get_media(fileId=file_id)
    
    with open(destination, "wb") as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% complete.")

def download_ran_file(row, drive_service, parentDir_id=None):
    """
    Processes 'ran' task to extract duration, stimulus, and video paths.
    """
    try:
        
        audio_file = row['audio_file']   
        parentDir = row['parentDir']

        module_dir = Path(__file__).resolve().parent

        # Construct the full path to data/raw
        data_raw_dir = module_dir / 'audio_data'

        # Make sure the directory exists
        data_raw_dir.mkdir(parents=True, exist_ok=True)

        if os.path.exists(data_raw_dir / parentDir / audio_file):
            print(f"{parentDir}/{audio_file} already in data/raw")
            
        else:

            if parentDir_id == None:
                parentDir_id = get_folder_id(folder_name=parentDir, drive_service=drive_service)
        
            file_id = search_file(audio_file, parentDir_id, drive_service)
            download_file(file_id, drive_service, data_raw_dir / parentDir / audio_file)

    except KeyError as e:
        print(f"Error processing RAN task for file at {parentDir}/{audio_file}: {e}")


def test():

    module_dir = Path(__file__).resolve().parent
    print(module_dir)

    data_raw_dir = module_dir / 'data' / 'raw'
    print(data_raw_dir)

    return Path(__file__).resolve().parent


test()