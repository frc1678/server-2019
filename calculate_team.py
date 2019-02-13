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

def team_calculations(timds):
    """Calculates all the calculated data for one team.

    Uses a team's timds to make many calculations and return them in a
    dictionary of calculatedData, the same that is used when exporting
    to the firebase later on.
    timds is the list of timds that a team has participated in, this is
    where the data comes from when making calculations."""
    calculated_data = {}

    calculated_data['hasOrangeGroundIntake'] = True if [
        action for timd in timds for action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'orange' and
        action.get('zone') != 'leftLoadingStation' and
        action.get('zone') != 'rightLoadingStation'] else False

    return calculated_data

# Uses the team number to find all the TIMDs for the passed team.
TIMDS = []
for timd in os.listdir(utils.create_file_path('data/cache/timds')):
    if TEAM_NUMBER in timd:
        with open(utils.create_file_path(
                f'data/cache/timds/{timd}')) as timd_file:
            TIMDS.append(timd_file.read())

FINAL_TEAM_DATA = team_calculations(TIMDS)

# Save data in local cache
with open(utils.create_file_path(f'data/teams/{TEAM_NUMBER}.json'),
          'w') as file:
    json.dump(FINAL_TEAM_DATA, file)

# Save data in Firebase upload queue
with open(utils.create_file_path(
        f'data/upload_queue/teams/{TEAM_NUMBER}.json'), 'w') as file:
    json.dump(FINAL_TEAM_DATA, file)
