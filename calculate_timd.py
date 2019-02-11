#!/usr/bin/python3.7
"""Calculations for a single TIMD.

TIMD stands for Team In Match Data.  TIMD calculations include
consolidation of (up to) 3 tempTIMDs (temporary TIMDs) into a single
TIMD, and the calculation of data points that are reflective of a team's
performance in a single match.

Consolidation is the process of determining the actions a robot
performed in a match by using data from (up to) 3 tempTIMDs.  One
tempTIMD is created per scout per match.  Ideally, 18 scouts are
distributed evenly across the 6 robots per match, resulting in 3
tempTIMDs per robot per match (aka 3 tempTIMDs per TIMD).  However, the
number of tempTIMDs per TIMD may be less than 3, depending on scout
availability, incorrect scout distribution, or missing data.

Called by server.py with the name of the TIMD to be calculated."""
# External imports
import json
import os
import sys
# Internal imports
import consolidation
import decompress
import utils

# Check to ensure TIMD name is being passed as an argument
if len(sys.argv) == 2:
    # Extract TIMD name from system argument
    TIMD_NAME = sys.argv[1]
else:
    print('Error: TIMD name not being passed as an argument. Exiting...')
    sys.exit(0)

COMPRESSED_TIMDS = []

TEMP_TIMDS = {'CARL' : {
    'startingLevel': 2,
    'crossedHabLine': True,
    'startingLocation': 'mid',
    'preload' : 'lemon',
    'driverStation': 1,
    'isNoShow': False,
    'timerStarted': 1547528330,
    'currentCycle': 4,
    'scoutID': 7,
    'scoutName': 'Carl',
    'appVersion': '1.2',
    'assignmentMode': 'QR',
    'assignmentFileTimestamp': 1547528290,
    'matchesNotScouted': [1, 14, 28, 35],
    'timeline': [
        {
            'type': 'intake',
            'time' : '102.4',
            'piece': 'orange',
            'zone': 'rightLoadingStation',
            'didSucceed': True,
            'wasDefended': False,
        },
        {
            'type': 'incap',
            'time': '109.6',
            'cause': 'brokenMechanism',
        },
        {
            'type': 'unincap',
            'time': '111.1',
        },
        {
            'type': 'drop',
            'time': '112.1',
            'piece': 'orange',
        },
        {
            'type': 'intake',
            'time': '120',
            'piece': 'lemon',
            'zone': 'zone2Left',
            'didSucceed': True,
            'wasDefended': True,
        },
        {
            'type': 'placement',
            'time': '127.4',
            'piece': 'orange',
            'didSucceed': False,
            'wasDefended': False,
            'shotOutOfField': True,
            'structure': 'leftRocket',
            'side': 'right',
            'level': 2,
        },
        {
            'type': 'spill',
            'time': '130',
            'piece': 'lemon',
        },
        {
            'type': 'climb',
            'time': '138',
            'attempted': {'self': 3, 'robot1': 3, 'robot2': 2},
            'actual': {'self': 3, 'robot1': 2, 'robot2': 1},
        }
    ],
}}

def add_calculated_data_to_timd(timd):
    """Calculates data in a timd and adds it to 'calculatedData' in the TIMD.

    timd is the TIMD that needs calculated data."""
    calculated_data = {}

    # Adds counting data points to calculated data, does this by setting
    # the key to be the sum of a list of ones, one for each time the
    # given requirements are met. This creates the amount of times those
    # requirements were met in the timeline.
    calculated_data['orangesScored'] = sum([
        1 for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('didSucceed') is True and
        action.get('piece') == 'orange'])
    calculated_data['lemonsScored'] = sum([
        1 for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('didSucceed') is True and
        action.get('piece') == 'lemon'])
    calculated_data['orangeFouls'] = sum([
        1 for action in timd.get('timeline') if
        action.get('shotOutOfField') is True])
    calculated_data['lemonsSpilled'] = sum([
        1 for action in timd.get('timeline') if
        action.get('type') == 'spill'])

    timd['calculatedData'] = calculated_data

    return timd

# Goes into the temp_timds folder to get the names of all the tempTIMDs
# that correspond to the given TIMD.
for temp_timd in os.listdir(utils.create_file_path('data/cache/temp_timds')):
    if TIMD_NAME in temp_timd:
        file_path = utils.create_file_path(
            'data/cache/temp_timds/' + temp_timd)
        with open(file_path, 'r') as compressed_temp_timd:
            COMPRESSED_TIMDS.append(compressed_temp_timd.read())
'''
# Iterates through all the compressed tempTIMDs and decompresses them.
# After decompressing them, adds them to the TEMP_TIMDS dictionary with
# the scout name as the key and their decompressed tempTIMD as a value.
# Does this in order to have a proper input to the consolidation
# function.
for compressed_temp_timd in COMPRESSED_TIMDS:
    decompressed_temp_timd = decompress.decompress_temp_timd(
        compressed_temp_timd)
    TEMP_TIMDS[decompressed_temp_timd.get(
        'scoutName')] = decompressed_temp_timd
'''

# After the TEMP_TIMDS are decompressed, they are fed into the
# consolidation script where they are returned as one final TIMD. This
# final TIMD is set as the variable name UNCALCULATED_TIMD.
UNCALCULATED_TIMD = consolidation.consolidate_temp_timds(TEMP_TIMDS)

# Defines FINAL_TIMD as a version of the TIMD with calculated data
# using the add_calculated_data_to_timd function at the top of the file.
FINAL_TIMD = add_calculated_data_to_timd(UNCALCULATED_TIMD)

# Save data in local cache
with open(utils.create_file_path('data/timds/' + TIMD_NAME + '.json'),
          'w') as file:
    json.dump(FINAL_TIMD, file)

# Save data in Firebase upload queue
with open(utils.create_file_path('data/upload_queue/timds/' + TIMD_NAME +
                                 '.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)
