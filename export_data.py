"""Exports Team and TIMD data to CSV files for picklist spreadsheet.

Team data is saved in 'data/exports/export-TEAM.csv'
TIMD data is saved in 'data/exports/export-TIMD.csv'
The picklist spreadsheet is in Google Sheets.  Each CSV file is imported
into a different sheet."""
# External imports
import csv
import time
# Internal imports
import firebase_communicator

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
TEAM_KEYS = ['teamNumber'] + list(TEAM_KEYS)

print(TIMD_KEYS)
print("")
print(TEAM_KEYS)
