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
#!/usr/bin/python3.7
# External imports
import json
import os
import sys
# Internal imports
import utils

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Check to ensure TIMD name is being passed as an argument
if len(sys.argv) == 2:
    # Extract TIMD name from system argument
    TIMD_NAME = sys.argv[1]
else:
    print('Error: TIMD name not being passed as an argument. Exiting...')
    sys.exit(0)

#TODO: Open tempTIMD data

#TODO: Do calculations

FINAL_TIMD = {}

# Save data in local cache
with open(utils.create_file_path('data/timds/' + TIMD_NAME + '.json'),
          'w') as file:
    json.dump(FINAL_TIMD, file)

# Save data in Firebase upload queue
with open(utils.create_file_path('data/upload_queue/timds' + TIMD_NAME +
                                 '.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)
