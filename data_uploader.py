"""File to upload data to the firebase from the cached data files
inside the server-2019 folder.

Searches through /upload_queue for data that needs to be uploaded
since its last calculation, and sends it to firebase.
"""

#External Imports
#Internal Imports
import firebase_communicator
from utils import create_file_path

#Setting up firebase to be dealt with later
DB = firebase_communicator.configure_firebase()

