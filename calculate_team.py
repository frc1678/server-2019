#!/usr/bin/python3.6
"""Calculations for a single Team.

Team calculations include the calculation of data points that are
reflective of a team's performance across all of their matches.

Called by server.py with the number of the Team to be calculated."""
# External imports
import json
import os
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

# Uses the team number to find all the TIMDs for the passed team.
TIMDS = []
for timd in os.listdir(utils.create_file_path('data/cache/timds')):
    if TEAM_NUMBER in timd:
        with open(utils.create_file_path(
                f'data/cache/timds/{timd}')) as timd_file:
            TIMDS.append(timd_file.read())

#TODO: Do calculations

FINAL_TEAM_DATA = {}

# Save data in local cache
with open(utils.create_file_path(f'data/teams/{TEAM_NUMBER}.json'),
          'w') as file:
    json.dump(FINAL_TEAM_DATA, file)

# Save data in Firebase upload queue
with open(utils.create_file_path(
        f'data/upload_queue/teams/{TEAM_NUMBER}.json'), 'w') as file:
    json.dump(FINAL_TEAM_DATA, file)
