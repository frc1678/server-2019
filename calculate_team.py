#!/usr/bin/python3.7
"""Calculations for a single Team.

Team calculations include the calculation of data points that are
reflective of a team's performance across all of their matches.

Called by server.py with the number of the Team to be calculated."""
# External imports
import json
import sys
# Internal imports
import utils

# Check to ensure Team number is being passed as an argument
if len(sys.argv) == 2:
    # Extract Team number from system argument
    TEAM_NUMBER = int(sys.argv[1])
else:
    print('Error: Team number not being passed as an argument. Exiting...')
    sys.exit(0)

#TODO: Open TIMD data

#TODO: Do calculations

FINAL_TEAM_DATA = {}

# Save data in local cache
with open(utils.create_file_path('data/teams/' + TEAM_NUMBER + '.json'),
          'w') as file:
    json.dump(FINAL_TEAM_DATA, file)

# Save data in Firebase upload queue
with open(utils.create_file_path('data/upload_queue/teams/' + TEAM_NUMBER
                                 + '.json'), 'w') as file:
    json.dump(FINAL_TEAM_DATA, file)
