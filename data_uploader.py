"""File to upload data to the firebase from the cached data files
inside the server-2019 folder.

Searches through /upload_queue for data that needs to be uploaded
since its last calculation, and sends it to firebase.
"""

# External imports
import json
import os
# Internal imports
import firebase_communicator
import utils

# Uses default firebase URL
DB = firebase_communicator.configure_firebase()

def collect_file_data(data_file, root_key):
    """Collects data from the data_file and returns it."""
    # Assigns a variable to the data from the file.
    file_path = utils.create_file_path(data_file)
    with open(file_path, 'r') as file_data:
        file_data = json.load(file_data)

    # Defines the file name for later use.
    file_name = data_file.split('.')[0].split('/')[-1]

    # Iterates through all the data points inside the file and
    # creates keys on the FINAL_DATA dictionary with keys in the
    # format of /root firebase key/key/datapoint to export later.
    path_data = {}
    for data_field, data_value in file_data.items():
        path_data[os.path.join(root_key, file_name, data_field)] = data_value
    return path_data

# Creates the final dictionary that is sent to firebase in one large
# pyrebase request.
FINAL_DATA = {}

# Creates a dictionary mapping all the firebase keys to the cache
# directory keys.
FIREBASE_TO_CACHE_KEY = {
    'TeamInMatchDatas': 'timds',
    'Matches': 'matches',
    'Teams': 'teams'
}

# Adds all the files to the UPLOAD_QUEUES dictionary. Does this by
# first iterating through the three upload queues, then iterating
# through all the files in the queue. Then, it adds each file path
# to the list inside the UPLOAD_QUEUES dictionary in the format of
# data/upload_queue/directory/file_name.
for firebase_key, cache_key in FIREBASE_TO_CACHE_KEY.items():
    for file in os.listdir(utils.create_file_path(
            'data/upload_queue/' + cache_key)):
        queue_file_path = os.path.join('data/upload_queue/', cache_key, file)

        # After the path is determined, collects data and uses it to
        # update the FINAL_DATA dictionary.
        FINAL_DATA.update(collect_file_data(queue_file_path, firebase_key))

# Sends the data to firebase.
DB.update(FINAL_DATA)
