"""Updates assignments when the cycle number is changed."""
#!/usr/bin/python3.7
# External imports
import json
import sys
# Internal imports
import firebase_communicator
import utils

# Uses default firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

if len(sys.argv) == 2:
    CYCLE_NUMBER = sys.argv[1]
else:
    print('Error: Cycle number not being passed as an argument. Exiting...')
    sys.exit(0)

# Each scout name is associated with a letter (for compression).
# This opens the JSON file that stores the letters and loads the dict
# that is used to swap names with letters.
with open(utils.create_file_path('letters.json'), 'r') as file:
    LETTERS = json.load(file)

AVAILABILITY = DB.child('scoutManagement/availability').get().val()

AVAILABLE_SCOUTS = [scout for scout, availability in AVAILABILITY.items()
                    if availability == 1]

ASSIGNMENT_STRING = CYCLE_NUMBER + '|'
# Currently, this assigns in no particular order.
# This is temporary until SPRs are implemented.
for scout in AVAILABLE_SCOUTS:
    ASSIGNMENT_STRING += LETTERS[scout]

DB.child('scoutManagement/QRcode').set(ASSIGNMENT_STRING)
