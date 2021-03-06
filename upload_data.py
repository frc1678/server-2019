#!/usr/bin/python3.6
"""Uploads data from files in the 'upload_queue' directory to firebase.

The 'upload_queue' directory contains three directories: 'timds',
'teams', and 'matches'.  Collects data from each of these three
directories and sends it to firebase in a single request."""
# External imports
import json
import os
# Internal imports
import firebase_communicator
import utils

# Uses default firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

def collect_file_data(file_path_, firebase_collection):
    """Converts local format to multi-location format for a single file.

    file_path_ is the absolute path to the file
    firebase_collection refers to a collection on Firebase (must be
    'TIMDs', 'Teams', or 'Matches')"""
    if firebase_collection not in ['TIMDs', 'Teams', 'Matches']:
        print(f"Error: '{firebase_collection}' is not a Firebase collection")
        return {}

    with open(file_path_, 'r') as file_:
        file_data = json.load(file_)

    # Extracts document name (removes '.json' ending and parent directories)
    # (e.g. "1678Q3" [TIMD] or "1" [Match])
    document_name = file_path_.split('.')[0].split('/')[-1]

    multi_location_data = {}
    # Converts data from local format to the Pyrebase multi-location
    # update format.
    # Pyrebase multi-location update key:value format:
    # "/<firebase-collection>/<document-name>/<data-field>": <data-value>
    # (e.g. /TIMDs/1678Q3/startingLocation": "left")
    for data_field, data_value in file_data.items():
        # NOTE: This code re-defines variables outside of its scope and
        # its behavior may differ from its appearance.
        # TODO: Clean up variable names
        if isinstance(data_value, dict):
            for key, value_ in data_value.items():
                if isinstance(key, dict):
                    # NOTE: This if-block probably doesn't trigger,
                    # since a key cannot be a dict.
                    for key2, value2 in value_.items():
                        path = os.path.join(data_field, key2)
                        value = value2
                        multi_location_data[os.path.join(firebase_collection, \
                            document_name, path)] = value
                else:
                    path = os.path.join(data_field, key)
                    value = value_
                    multi_location_data[os.path.join(firebase_collection, \
                        document_name, path)] = value
        else:
            path = data_field
            value = data_value
            multi_location_data[os.path.join(firebase_collection, \
                document_name, path)] = value
    return multi_location_data

FINAL_DATA = {}

# Firebase key names to the equivilent local cache key names
FIREBASE_TO_CACHE_KEY = {
    'TIMDs': 'timds',
    'Teams': 'teams',
    'Matches': 'matches',
}

FILES_TO_REMOVE = []

for firebase_key, cache_key in FIREBASE_TO_CACHE_KEY.items():
    for file in os.listdir(utils.create_file_path(
            f'data/upload_queue/{cache_key}')):
        file_path = utils.create_file_path(
            f'data/upload_queue/{cache_key}/{file}')
        # Collects and adds the data from a single file to 'FINAL_DATA'
        FINAL_DATA.update(collect_file_data(file_path, firebase_key))

        FILES_TO_REMOVE.append(file_path)

# Before sending the data, iterates through all of it and removes any
# NaNs (Not a Number) in the data.  (Relies on NaN != NaN)
# HACK: NaNs should be handled during calculation.
for path, value in FINAL_DATA.items():
    if path.split('/')[-1] == 'timeline':
        for action in value:
            for key, value_ in action.items():
                if isinstance(value_, float) and value_ != value_:
                    action[key] = None
    if isinstance(value, float) and value != value:
        FINAL_DATA[path] = None

# Sends the data to firebase.
DB.update(FINAL_DATA)

# Removes files after upload to prevent data loss
for file_path in FILES_TO_REMOVE:
    # Removes the file from the upload queue to prevent re-upload
    os.remove(file_path)
