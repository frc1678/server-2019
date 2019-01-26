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

# Creating three variables assigned to each of the directories in the
# /server-2019/data/upload_queue pathway, which are later iterated upon
# to find all the files needed to upload.
TIMD_UPLOAD_QUEUE = utils.create_file_path('data/upload_queue/timds/')
MATCH_UPLOAD_QUEUE = utils.create_file_path('data/upload_queue/matches/')
TEAM_UPLOAD_QUEUE = utils.create_file_path('data/upload_queue/teams/')

def collect_file_data(queue_path, root_key):
    """Iterates through the data that need to be sent from the queue path
    provided as an argument, then collects them in a dictionary. This
    dictionary is then added to the final dictionary."""
    for data_file in os.listdir(queue_path):

        # Assigns a variable to the data from the file.
        file_path = os.path.join(queue_path, data_file)
        with open(file_path, 'r') as file_data:
            file_data = json.load(file_data)

        # Defines the file name for later use.
        file_name = data_file.split('.')[0]

        # If the name of the file doesn't match with the initial key
        # (The key inside the file whose value is the timd) of the file,
        # it throws an error and continues on to process other files.
        # This would occur when the mechanism that sends to the cache
        # files fails and sends the wrong timd name.
        if file_name != list(file_data)[0]:
            print(f"Error: File name '{data_file.split('.')[0]}' does not match top-level key '{list(file_data)[0]}'.  Exiting...")
        # If the name does match, it puts the data in a large dictionary
        # with the form of /Teams/teamnumber/datapoint to export later.
        else:
            path_data = {}
            for data_field, data_value in file_data[file_name].items():
                path_data[os.path.join(root_key, file_name, data_field)] = data_value
            FINAL_DATA.update(path_data)


# Creates the final dictionary that is sent to firebase in one large
# pyrebase request.
FINAL_DATA = {}

# Collects all the data from the three seperate queues into the
# FINAL_DATA dictionary in order to be sent.
collect_file_data(TIMD_UPLOAD_QUEUE, 'TeamInMatchDatas')
collect_file_data(MATCH_UPLOAD_QUEUE, 'Matches')
collect_file_data(TEAM_UPLOAD_QUEUE, 'Teams')

# Sends the data to firebase.
DB.update(FINAL_DATA)
