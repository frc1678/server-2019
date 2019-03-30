#!/usr/bin/python3.6
"""Forwards tempSuper data to Matches and TIMD.

Sends to 'matches' and 'timds' in the local cache, and to 'Matches' and
'TIMDs' on Firebase.

'tempSuper', 'Matches', and 'TIMDs' are collections on Firebase."""
# External imports
import json
import os
# Internal imports
import decompressor
import firebase_communicator
import utils

# Uses default firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

# List of files (tempSuper datas) in the 'temp_super' cache directory.
TEMP_SUPER_FILES = os.listdir(utils.create_file_path('data/cache/temp_super'))

for temp_super_file in TEMP_SUPER_FILES:
    with open(utils.create_file_path(
            f'data/cache/temp_super/{temp_super_file}'), 'r') as file:
        compressed_temp_super = file.read()
    # Removes trailing newline (if it exists) from file data.
    # Many file editors will automatically add a newline at the end of files.
    compressed_temp_super = compressed_temp_super.rstrip('\n')

    decompressed_temp_super = \
        decompressor.decompress_temp_super(compressed_temp_super)


    temp_super_key = list(decompressed_temp_super)[0]
    # 'temp_super_headers' still contains team data
    temp_super_headers = decompressed_temp_super[temp_super_key]
    temp_super_teams = {}

    for team in ['team1', 'team2', 'team3']:
        # Removes team data from 'temp_super_headers' and adds it to
        # 'temp_super_teams'
        temp_super_teams[team] = temp_super_headers.pop(team)

    # Extracts 'match_number' from tempSuper key (e.g. 'S!Q1-B' to '1')
    # 'match_number' is a string
    match_number = temp_super_key.split('Q')[1].split('-')[0]


    # Sends 'temp_super_teams' to TIMDs local cache and upload queue.
    for team in temp_super_teams.values():
        # TIMD name format example: '1678Q3' (1678 is the team number, 3
        # is the match number)
        timd_name = f"{team['teamNumber']}Q{match_number}"
        timd_file_path = f'data/cache/timds/{timd_name}.json'
        try:
            with open(utils.create_file_path(timd_file_path), 'r') as file:
                timd_data = json.load(file)
        except FileNotFoundError:
            timd_data = {}

        # HACK: 'teamNumber' and 'matchNumber' must exist for all TIMDs,
        # including those with only super data + not scout data.
        timd_data['teamNumber'] = int(team['teamNumber'])
        timd_data['matchNumber'] = int(match_number)
        team['teamNumber'] = int(team['teamNumber'])
        team['matchNumber'] = int(match_number)
        # Adds tempSuper data to any previous TIMD data
        timd_data.update(team)
        with open(utils.create_file_path(timd_file_path), 'w') as file:
            json.dump(timd_data, file)

        # Sends team data to upload queue.  upload_data.py will
        # automatically update the data on Firebase, so we don't need to
        # send the 'timd_data' that was read from the file.
        with open(utils.create_file_path(
                f'data/upload_queue/timds/{timd_name}.json'), 'w') as file:
            json.dump(timd_data, file)


    # Sends 'temp_super_headers' to Matches local cache and upload queue.

    alliance = temp_super_key.split('-')[1]
    if alliance == 'B':
        alliance = 'blue'
    else:
        alliance = 'red'
    # Re-structure alliance-specific data fields
    # (e.g. 'cargoShipPreloads' to 'redCargoShipPreloads')
    temp_super_headers[f'{alliance}CargoShipPreloads'] = \
        temp_super_headers.pop('cargoShipPreloads')
    temp_super_headers[f'{alliance}NoShowTeams'] = \
        temp_super_headers.pop('noShowTeams')

    # Re-structures tempSuper-specific data fields
    # tempSuper data field name to Match data field name
    header_conversion = {
        'redScore': 'redActualScore',
        'blueScore': 'blueActualScore',
    }
    for super_field_name, match_field_name in header_conversion.items():
        if temp_super_headers.get(super_field_name) is not None:
            temp_super_headers[match_field_name] = temp_super_headers.pop(
                super_field_name)

    # Sends 'temp_super_headers' to Matches local cache and Firebase.
    match_file_path = f'data/cache/matches/{match_number}.json'
    try:
        with open(utils.create_file_path(match_file_path), 'r') as file:
            match_data = json.load(file)
    except FileNotFoundError:
        match_data = {}

    for key, value in temp_super_headers.items():
        # If the data field does not exist we should update it since we
        # have not received data from TBA for the data field.
        if match_data.get(key) is None:
            match_data[key] = value

    # Saves complete data to local cache
    with open(utils.create_file_path(match_file_path), 'w') as file:
        json.dump(match_data, file)

    # Saves complete data in upload queue
    with open(utils.create_file_path(
            f'data/upload_queue/matches/{match_number}.json'), 'w') as file:
        json.dump(match_data, file)
