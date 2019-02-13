#!/usr/bin/python3.6
"""Prepares Firebase for competition."""
# External imports
import sys
# Internal imports
import firebase_communicator
import tba_communicator

def request_input(message, true_values, false_values):
    """Requests user input and returns a boolean.

    The function will return True if the input is in 'true_values',
    False if the input is in 'false_values', and will otherwise ask for
    input again.

    message is the string to show to user when asking for input
    true_values is a list of strings
    false_values is a list of strings"""
    while True:
        # Uses '.lower()' to be case-insensitive
        user_input = input(message).lower()
        if user_input in true_values:
            return True
        elif user_input in false_values:
            return False
        else:
            print('Press CTRL+C to exit')

# User input
PREPARE_TEAMS = request_input(
    'Prepare teams? (y/n): ', ['y', 'yes'], ['n', 'no'])
PREPARE_MATCHES = request_input(
    'Prepare matches? (y/n): ', ['y', 'yes'], ['n', 'no'])

if PREPARE_TEAMS is True and PREPARE_MATCHES is True:
    MESSAGE = 'TEAMS and MATCHES'
elif PREPARE_TEAMS is True:
    MESSAGE = 'TEAMS'
elif PREPARE_MATCHES is True:
    MESSAGE = 'MATCHES'
else:
    print('\nError: No collections were selected to prepare.  Exiting...')
    sys.exit(0)

# User confirmation
print(f'\nWarning: {MESSAGE} will be wiped from Firebase!')
CONFIRMATION = request_input("Type 'wipe' to continue: ", ['wipe'], [])

# Retrieves data from TBA
if PREPARE_TEAMS is True:
    TEAMS = tba_communicator.request_teams()
if PREPARE_MATCHES is True:
    MATCHES = tba_communicator.request_matches()
print('\nAll TBA data successfully retrieved.')

# TODO: Wipe certain Firebase collections
# TODO: Populate Firebase with Teams and Matches
# TODO: Populate TBA data fields with -1
