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

if TIMD_DATA is None:
    print('Warning: TIMD data does not exist on Firebase')
else:
    print('TIMD data successfully retrieved')
if TEAM_DATA is None:
    print('Warning: Team data does not exist on Firebase')
else:
    print('Team data successfully retrieved')

# Extracts TIMD data field keys by adding the keys of all TIMDs to a set
TIMD_KEYS = set()
for timd_value in TIMD_DATA.values():
    for key in timd_value:
        if key == 'calculatedData':
            # Adds data fields that are nested in 'calculatedData'
            TIMD_KEYS = TIMD_KEYS.union(timd_value['calculatedData'].keys())
        else:
            TIMD_KEYS.add(key)

# Converts 'TIMD_KEYS' to a list since 'matchNumber' needs to be the
# first item and 'teamNumber' needs to be the second item (for the
# spreadsheet)
TIMD_KEYS.discard('matchNumber')
TIMD_KEYS.discard('teamNumber')
TIMD_KEYS = ['matchNumber', 'teamNumber'] + list(TIMD_KEYS)

# Extracts Team data field keys by adding the keys of all Teams to a set
TEAM_KEYS = set()
for team_value in TEAM_DATA.values():
    for key in team_value:
        if key == 'calculatedData':
            # Adds data fields that are nested in 'calculatedData'
            TEAM_KEYS = TEAM_KEYS.union(team_value['calculatedData'].keys())
        else:
            TEAM_KEYS.add(key)

# Converts 'TEAM_KEYS' to a list since 'teamNumber' needs to be the
# first item (for the spreadsheet)
TEAM_KEYS.discard('teamNumber')
TEAM_KEYS = ['teamNumber'] + list(TEAM_KEYS)

with open(utils.create_file_path('data/exports/export-TIMD.csv'), 'w') as file:
    CSV_WRITER = csv.DictWriter(file, fieldnames=TIMD_KEYS)
    CSV_WRITER.writeheader()
    for timd_value in TIMD_DATA.values():
        # Un-nests data fields nested in 'calculatedData', removes
        # 'calculatedData' key
        timd_value.update(timd_value.pop('calculatedData', {}))
        CSV_WRITER.writerow(timd_value)

with open(utils.create_file_path('data/exports/export-TEAM.csv'), 'w') as file:
    CSV_WRITER = csv.DictWriter(file, fieldnames=TEAM_KEYS)
    CSV_WRITER.writeheader()
    for team_value in TEAM_DATA.values():
        # Un-nests data fields nested in 'calculatedData', removes
        # 'calculatedData' key
        team_value.update(team_value.pop('calculatedData', {}))
        CSV_WRITER.writerow(team_value)

print("Data successfully exported to the 'data/exports' directory")
