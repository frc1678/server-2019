#!/usr/bin/python3.6
"""Prepares Firebase for competition.

Sends blank 'Teams' and 'Matches' to Realtime Database.
Sends blank 'Teams' to Cloud Firestore."""
# External imports
import sys
# Internal imports
import firebase_communicator
import firestore_communicator
import tba_communicator

# 'FIREBASE' is a Realtime Database instance
FIREBASE = firebase_communicator.configure_firebase('ccsaposs-dev')
# 'FIRESTORE' is a Cloud Firestore database instance
FIRESTORE = firestore_communicator.configure_cloud_firestore()

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

FULL_WIPE = request_input("Wipe entire database? (y/n): ", ['y', 'yes'],
                          ['n', 'no'])

if FULL_WIPE is True:
    PREPARE_TEAMS = True
    PREPARE_MATCHES = True
    MESSAGE = 'EVERYTHING'
else:
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

# Data to be uploaded to the Realtime Database
FIREBASE_UPLOAD = {}

if PREPARE_TEAMS is True:
    FINAL_TEAM_DATA = {}
    for team in TEAMS:
        team_number = team['team_number']
        team_name = team['nickname']
        FINAL_TEAM_DATA[team_number] = {
            'teamNumber': team_number,
            'name': team_name,
        }
    FIREBASE_UPLOAD.update({'Teams': FINAL_TEAM_DATA})

if PREPARE_MATCHES is True:
    FINAL_MATCH_DATA = {}
    for match_data in MATCHES:
        # 'qm' stands for qualification match
        if match_data['comp_level'] == 'qm':
            red_teams = match_data['alliances']['red']['team_keys']
            blue_teams = match_data['alliances']['blue']['team_keys']
            match_number = match_data['match_number']
            # Remove 'frc' from team number and convert to integer
            # (e.g. 'frc1678' -> 1678)
            red_teams = [int(team[3:]) for team in red_teams]
            blue_teams = [int(team[3:]) for team in blue_teams]
            FINAL_MATCH_DATA[match_number] = {
                'matchNumber': match_number,
                'redTeams': red_teams,
                'blueTeams': blue_teams,
            }
    FIREBASE_UPLOAD.update({'Matches': FINAL_MATCH_DATA})

if FULL_WIPE is True:
    FIREBASE_UPLOAD.update({
        'tempTIMDs': None,
        'TIMDs': None,
        'tempSuper': None,
        'scoutManagement': {
            'currentMatchNumber': 1,
            'cycleNumber': 0,
        }
    })

# Sends data to Firebase
FIREBASE.update(FIREBASE_UPLOAD)

# Sends data to Cloud Firestore
if PREPARE_TEAMS is True:
    print('Retriving data from Firestore...')
    TEAMS = FIRESTORE.collection('Teams').get()
    print('Data successfully retrieved from Firestore.')

    # Combine requests into a single batch
    BATCH = FIRESTORE.batch()

    # Removes teams that already exist on Cloud Firestore
    for team in TEAMS:
        BATCH.delete(FIRESTORE.collection('Teams').document(team.id))

    # Adds data in 'FINAL_TEAM_DATA'
    for team_number, team_value in FINAL_TEAM_DATA.items():
        BATCH.set(FIRESTORE.collection('Teams').document(str(team_number)),
                  team_value)

    # Sends batch request
    BATCH.commit()
