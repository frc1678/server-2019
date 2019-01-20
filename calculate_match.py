#!/usr/bin/python3.7
"""Calculations for a single Match.

Match calculations include predictions of the outcome (i.e. score and
ranking points by alliance) of a match.

Called by server.py with the number of the Match to be calculated."""
# External imports
import json
import sys
# Internal imports
import utils

# Check to ensure Match number is being passed as an argument
if len(sys.argv) == 2:
    # Extract Match number from system argument
    MATCH_NUMBER = sys.argv[1]
else:
    print('Error: Match number not being passed as an argument. Exiting...')
    sys.exit(0)

#TODO: Open Team (and possibly TIMD) data

#TODO: Do calculations

FINAL_MATCH_DATA = {}

# Save data in local cache
with open(utils.create_file_path('data/matches/' + MATCH_NUMBER + '.json'),
          'w') as file:
    json.dump(FINAL_MATCH_DATA, file)

# Save data in Firebase upload queue
with open(utils.create_file_path('data/upload_queue/matches' + MATCH_NUMBER +
                                 '.json'), 'w') as file:
    json.dump(FINAL_MATCH_DATA, file)
