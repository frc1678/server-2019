#!/usr/bin/python3.6
"""Updates assignments when the cycle number is changed."""
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
with open(utils.create_file_path('data/assignments/assignments.json'), 'r') as file:
    LETTERS = json.load(file)['letters']

AVAILABILITY = DB.child('scoutManagement/availability').get().val()

AVAILABLE_SCOUTS = [scout for scout, availability in AVAILABILITY.items()
                    if availability == 1]

ASSIGNMENT_STRING = f'{CYCLE_NUMBER}|'

with open(utils.create_file_path('data/sprs/sprs.json'), 'r') as file:
    SPRS = json.load(file)

# Sorts scouts from best SPR to worst SPR
# Scouts without SPRs default to 0.0, since we want them to be placed
# with other scouts.  (Scouts with a lower SPR are more likely to be in
# groups of 3)
AVAILABLE_SCOUTS.sort(key=lambda scout: SPRS.get(scout, {}).get(
    'overall', 0.0), reverse=True)

for scout in AVAILABLE_SCOUTS:
    ASSIGNMENT_STRING += LETTERS[scout]

DB.child('scoutManagement/QRcode').set(ASSIGNMENT_STRING)
