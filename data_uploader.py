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

def collect_file_data(data_file, root_key):
    """Organizes and returns each data point from data_file as a firebase path.

    Takes data from the file passed as an argument, and forms each of
    the data points inside the file into a pathway added as a key to a
    dictionary which is returned. The pathway is the path to a specific
    data point on firebase where the data point is eventually sent to.
    The passed argument data_file is the absolute path of the specific
    file that data is taken from. root_key is one of the main
    collections on the firebase in which the data is eventually sent,
    limited to only 'Teams', Matches', and 'TeamInMatchDatas'. """
    with open(data_file, 'r') as file_:
        file_data = json.load(file_)

    # Defines the file name for to use when defining keys in the
    # path_data dictionary.
    file_name = data_file.split('.')[0].split('/')[-1]

    # Iterates through all the data points inside the file and creates
    # keys on the FINAL_DATA dictionary with keys in the format of
    # /root firebase key/key/datapoint to export later.
    path_data = {}
    for data_field, data_value in file_data.items():
        path_data[os.path.join(root_key, file_name, data_field)] = data_value
    return path_data

FINAL_DATA = {}

# Creates a dictionary mapping all the firebase keys to the cache
# directory keys.
FIREBASE_TO_CACHE_KEY = {
    'TeamInMatchDatas': 'timds',
    'Matches': 'matches',
    'Teams': 'teams'
}

# Iterates through the different directories inside the 'upload_queue'
# directory, then iterates through each of the files in each directory
# and runs collect_file_data on each file and adds the returned data to
# the FINAL_DATA dictionary.
for firebase_key, cache_key in FIREBASE_TO_CACHE_KEY.items():
    for file in os.listdir(utils.create_file_path(
            'data/upload_queue/' + cache_key)):
        queue_file_path = utils.create_file_path('data/upload_queue/' +
                                                 cache_key + '/' + file)

        # After the path is determined, collects data and uses it to
        # update the FINAL_DATA dictionary.
        FINAL_DATA.update(collect_file_data(queue_file_path, firebase_key))

# Sends the data to firebase.
DB.update(FINAL_DATA)
