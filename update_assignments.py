"""Updates assignments when the cycle number is changed."""
#!/usr/bin/python3.7
# External imports
import json
import os
import sys
# Internal imports
import firebase_communicator

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Uses default firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

if len(sys.argv) > 1:
    CYCLE_NUMBER = sys.argv[1]
else:
    print('Error: Cycle number not being passed as an argument. Exiting...')
    sys.exit(0)

def create_file_path(path_after_main):
    """Joins the path of the directory this script is in with the path
    that is passed to this function.

    path_after_main is the path from inside the main directory.  For
    example, the path_after_main for server.py would be 'server.py'
    because it is located directly in the main directory."""
    return os.path.join(MAIN_DIRECTORY, path_after_main)

# Each scout name is associated with a letter (for compression).
# This opens the JSON file that stores the letters and loads the dict
# that is used to swap names with letters.
with open(create_file_path('letters.json'), 'r') as file:
    LETTERS = json.load(file)

AVAILABILITY = DB.child('availability').get().val()

AVAILABLE_SCOUTS = [scout for scout, availability in AVAILABILITY.items()
                    if availability == 1]

ASSIGNMENT_STRING = CYCLE_NUMBER + '|'
# Currently, this assigns in no particular order.
# This is temporary until SPRs are implemented.
for scout in AVAILABLE_SCOUTS:
    ASSIGNMENT_STRING += LETTERS[scout]

DB.child('QRcode').set(ASSIGNMENT_STRING)
