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
