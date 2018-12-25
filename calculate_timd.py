"""Updates assignments when the cycle number is changed."""
#!/usr/bin/python3.7
# External imports
import json
import os
import sys
# Internal imports
import utils

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) == 1:
    TIMD_NAME = sys.argv[1]
else:
    print('Error: TIMD name not being passed as an argument. Exiting...')
    sys.exit(0)

#TODO: Open tempTIMD data

#TODO: Do calculations

FINAL_TIMD = {}

with open(utils.create_file_path('data/timds/' + TIMD_NAME + '.json'),
          'w') as file:
    json.dump(FINAL_TIMD, file)
