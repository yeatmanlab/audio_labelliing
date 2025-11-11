import argparse
import os
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import google.auth
from pathlib import Path


def set_up_gdrive():
    """
    Initialize and authenticate a Google Drive API client.

    This function loads credentials from a provided Google Cloud service
    account key file and returns an authenticated Google Drive API service
    object that can be used to interact with Drive (e.g., list, download,
    or upload files).

    Parameters
    ----------
    Returns
    -------
    googleapiclient.discovery.Resource
        An authenticated Google Drive API service instance, initialized
        using the provided service account credentials.

    Notes
    -----
    The service is authorized with the scope:
    ``'https://www.googleapis.com/auth/drive'`` to allow read/write access.
    """

    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds, default_project = google.auth.default(scopes=SCOPES)
 
     # Dynamically switch quota project here:
    creds = creds.with_quota_project("som-nero-phi-jyeatman-webcam")
 
    drive_service = build('drive', 'v3', credentials=creds)

    return drive_service


def get_folder_id(folder_name, drive_service, parent_folder_id=None):
    """
    Search for a folder by name in Google Drive and return its ID.

    This function queries the Google Drive API for a folder with the given
    name, optionally restricting the search to a specified parent folder.
    If multiple folders share the same name, the first match is returned.

    Parameters
    ----------
    folder_name : str
        The name of the folder to search for.

    drive_service : googleapiclient.discovery.Resource
        An authenticated Google Drive API service instance.

    parent_folder_id : str, optional
        The ID of the parent folder to restrict the search. If None, the
        search is performed across all accessible Drive locations.

    Returns
    -------
    str or None
        The ID of the first matching folder if found, otherwise ``None``.
    """
    
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
    """
    Search for a specific file within a parent Google Drive folder.

    Parameters
    ----------
    filename : str
        The name of the file to search for.

    parent_folder_id : str
        The ID of the parent folder to search within.

    drive_service : googleapiclient.discovery.Resource
        An authenticated Google Drive API service instance.

    Returns
    -------
    str or None
        The file ID if found, otherwise ``None``.
    """
    query = f"name = '{filename}' and '{parent_folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    return files[0]['id'] if files else None

# Function to download a file
def download_file(file_id, drive_service, destination):
    """
    Download a file from Google Drive and save it to a local path.

    This function uses the Google Drive API to retrieve a file by its Drive
    file ID and save it to the specified destination on the local filesystem.
    The directory structure is created automatically if it does not exist.

    Parameters
    ----------
    file_id : str
        The Google Drive file ID of the file to be downloaded.

    drive_service : googleapiclient.discovery.Resource
        An authenticated Google Drive API service instance.

    destination : str or pathlib.Path
        The full local path where the file will be saved.

    Notes
    -----
    Prints download progress to the console while retrieving the file.
    """
    
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
    Download an audio file associated with a RAN (Rapid Automatized Naming) task.

    Given a row of file metadata from a dataframe, this function locates
    and downloads the associated audio file from Google Drive into the
    local ``audio_data`` directory. If the file already exists locally,
    it is skipped.

    Parameters
    ----------
    row : pandas.Series
        A row from a dataframe containing fields ``'audio_file'`` and
        ``'parentDir'``.

    drive_service : googleapiclient.discovery.Resource
        An authenticated Google Drive API service instance.

    parentDir_id : str, optional
        The Google Drive folder ID for the parent directory. If not
        provided, it will be fetched dynamically using ``get_folder_id()``.

    Raises
    ------
    KeyError
        If the expected keys (``'audio_file'``, ``'parentDir'``) are missing
        from the provided row.

    Notes
    -----
    Files are downloaded into ``<module_dir>/audio_data/<parentDir>/<audio_file>``.
    Existing files are not re-downloaded.
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