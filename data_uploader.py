"""File to upload data to the firebase from the cached data files
inside the server-2019 folder.

Searches through /upload_queue for data that needs to be uploaded
since its last calculation, and sends it to firebase.
"""

# External Imports
import os
import json
# Internal Imports
import firebase_communicator
from utils import create_file_path

# Setting up firebase to be dealt with later
DB = firebase_communicator.configure_firebase()

# Creating three variables assigned to each of the directories in the
# /server-2019/data/upload_queue pathway, which are later iterated upon
# to find all the files needed to upload.
TIMD_UPLOAD_QUEUE = create_file_path('data/upload_queue/timds/')
MATCH_UPLOAD_QUEUE = create_file_path('data/upload_queue/matches/')
TEAM_UPLOAD_QUEUE = create_file_path('data/upload_queue/teams/')

def collect_file_data(queue_path):
    """Iterates through the data that need to be sent, and collecting them
    in a dictionary."""
    final_dict = {}
    for data_file in os.listdir(queue_path):

        # Assigns a variable to the data from the file.
        file_path = create_file_path(os.path.join(queue_path, data_file))
        with open(file_path, 'r') as file_data:
            file_data = json.load(file_data)

        # If the name of the file doesn't match with the initial key of the
        # file, it throws an error and continues on to process other files.
        if data_file.split('.')[0] != list(file_data)[0]:
            print('Error: Data cannot be uploaded to firebase - Mismatching key and name')
        else:

        	# Otherwise, it puts the data in a large dictionary with the form
        	# of /Teams/1678/datapoint to export later.
            file_name = data_file.split('.')[0]
            path_data = {}
            for key, value in file_data[file_name].items():
                path_data[os.path.join(file_name, key)] = value
            final_dict.update(path_data)
    return final_dict

# Collects all the data into three seperate dictionaries to be sent to
# firebase.
FINAL_TIMDS = collect_file_data(TIMD_UPLOAD_QUEUE)
FINAL_MATCHES = collect_file_data(MATCH_UPLOAD_QUEUE)
FINAL_TEAMS = collect_file_data(TEAM_UPLOAD_QUEUE)

# Sends the data to firebase.
DB.child('TeamInMatchDatas').update(FINAL_TIMDS)
DB.child('Matches').update(FINAL_MATCHES)
DB.child('Teams').update(FINAL_TEAMS)
