#!/usr/bin/python3.6
"""Prepares Firebase for competition."""
# No external imports
# Internal imports
import firebase_communicator
import tba_communicator

# User confirmation
while True:
    print('\nWARNING: Firebase will be wiped!')
    CONFIRMATION = input("Type 'yes' to continue: ")
    # Uses '.lower()' to be case-insensitive
    if CONFIRMATION.lower() == 'yes':
        break
    else:
        print('Press CTRL+C to exit')


# TODO: Wipe certain Firebase collections
# TODO: Populate Firebase with Teams and Matches
# TODO: Populate TBA data fields with -1
