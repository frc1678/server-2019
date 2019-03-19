#!/usr/bin/python3.6
"""Exports Team and TIMD data to CSV files for picklist spreadsheet.

TIMD data is saved in 'data/exports/export-TIMD.csv'
Team data is saved in 'data/exports/export-TEAM.csv'
The picklist spreadsheet is in Google Sheets.  Each CSV file is imported
into a different sheet."""
# External imports
import csv
import time
# Internal imports
import firebase_communicator
import utils

# Uses default firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

def export_collection_data(collection_data, first_order_keys, csv_file_name):
    """Exports data from a Firebase collection to a CSV file.

    collection_data is the data from the Firebase collection
    first_order_keys are the keys (in order) that need to be displayed
    at the beginning (left) of the CSV file
    csv_file_name is the name to save the file as in '/data/exports'"""
    # Extracts collection data field keys by adding the keys of each
    # unique collection value to a set
    collection_keys = set()
    for collection_value in collection_data.values():
        for key in collection_value:
            if key == 'calculatedData':
                collection_keys = collection_keys.union(
                    collection_value['calculatedData'].keys())
            else:
                collection_keys.add(key)
    # Converts 'collection_keys' to a list since some keys need to
    # be at the beginning (left) of the CSV file (for the
    # spreadsheet)
    for key in first_order_keys:
        collection_keys.discard(key)
    collection_keys = first_order_keys + list(collection_keys)

    with open(utils.create_file_path(f'data/exports/{csv_file_name}'),
              'w') as file:
        csv_writer = csv.DictWriter(file, fieldnames=collection_keys)
        csv_writer.writeheader()
        for collection_value in collection_data.values():
            # Un-nests data fields nested in 'calculatedData', removes
            # 'calculatedData' key
            collection_value.update(collection_value.pop(
                'calculatedData', {}))
            csv_writer.writerow(collection_value)
        print(f"Data exported to 'data/exports/{csv_file_name}'")

print('Retrieving data from Firebase...')
while True:
    try:
        TIMD_DATA = DB.child('TIMDs').get().val()
        TEAM_DATA = DB.child('Teams').get().val()
    except OSError:
        print('Error: No internet connection.  Trying again in 3 seconds...')
    else:
        break
    time.sleep(3)

# Removes empty TIMDs
for timd in list(TIMD_DATA):
    if TIMD_DATA[timd].get('calculatedData') is None:
        TIMD_DATA.pop(timd)

if TIMD_DATA is None:
    print('Warning: TIMD data does not exist on Firebase')
else:
    print('TIMD data successfully retrieved')
    export_collection_data(TIMD_DATA, ['matchNumber', 'teamNumber'],
                           'export-TIMD.csv')

if TEAM_DATA is None:
    print('Warning: Team data does not exist on Firebase')
else:
    print('Team data successfully retrieved')
    export_collection_data(TEAM_DATA, ['teamNumber'], 'export-TEAM.csv')
