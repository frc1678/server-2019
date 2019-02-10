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
# Goes into the temp_timds folder to get the names of all the tempTIMDs
# that correspond to the given TIMD.
for temp_timd in os.listdir(utils.create_file_path('data/cache/temp_timds')):
    if TIMD_NAME in temp_timd:
        file_path = utils.create_file_path(
            'data/cache/temp_timds/' + temp_timd)
        with open(file_path, 'r') as compressed_temp_timd:
            COMPRESSED_TIMDS.append(compressed_temp_timd.read())

TEMP_TIMDS = {}
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

print(TEMP_TIMDS)
# Passes the TEMP_TIMDS through consolidation to create the one true
# TIMD used for later calculation.


#TODO: Do calculations

FINAL_TIMD = {}

# Save data in local cache
with open(utils.create_file_path('data/timds/' + TIMD_NAME + '.json'),
          'w') as file:
    json.dump(FINAL_TIMD, file)

# Save data in Firebase upload queue
with open(utils.create_file_path('data/upload_queue/timds/' + TIMD_NAME +
                                 '.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)
