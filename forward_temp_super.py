#!/usr/bin/python3.6
"""Forwards tempSuper data to Matches and TIMDs.

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

def avg_without_zeroes(lis):
    """Removes zeroes from a list, then returns the average of the list.

    lis is the list that is averaged"""
    lis = [item for item in lis if item != 0]
    if lis == []:
        return None
    else:
        return sum(lis)/len(lis)

# Uses default Firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

# List of files (tempSuper datas) in the 'temp_super' cache directory.
TEMP_SUPER_FILES = os.listdir(utils.create_file_path('data/cache/temp_super'))

# Match number (string) to list of tempSuper files for that match
FILES_BY_MATCH = {}
for file_name in TEMP_SUPER_FILES:
    # tempSuper naming format:
    # S!Q{match_number}-{alliance_color}
    # (e.g. S!Q3-B is the blue alliance in match 3)
    match_number = file_name.split('-')[0].split('Q')[1]
    if FILES_BY_MATCH.get(match_number) is None:
        FILES_BY_MATCH[match_number] = []
    FILES_BY_MATCH[match_number].append(file_name)

for match_number, files in FILES_BY_MATCH.items():
    compressed_data = {}
    for temp_super_file in files:
        # Possible values of 'alliance': 'R' (red) or 'B' (blue)
        alliance = temp_super_file.split('.')[0].split('-')[1]
        with open(utils.create_file_path(
                f'data/cache/temp_super/{temp_super_file}'), 'r') as file:
            compressed_data[alliance] = file.read()
    decompressed_data = {}
    for alliance, alliance_data in compressed_data.items():
        # Removes trailing newline (if it exists) from file data.
        # Many file editors will automatically add a newline at the end of files.
        alliance_data = alliance_data.rstrip('\n')
        decompressed_data[alliance] = list(
            decompressor.decompress_temp_super(alliance_data).values())[0]

    temp_super_teams = {}
    for alliance, alliance_data in decompressed_data.items():
        if alliance == 'R':
            opponent_alliance = 'B'
        else:
            opponent_alliance = 'R'
        for team in alliance_data:
            team_number = team['teamNumber']
            temp_super_teams[team_number] = {}
            for key in ['rankAgility', 'rankDefense', 'rankSpeed']:
                temp_super_teams[team_number][key] = team[key]
            temp_super_teams[team_number]['superTimeline'] = team['timeline']
            # Extracts defensive information for the 'team' from the
            # tempSuper data for the opposing alliance.
            opponent_data = decompressed_data.get(opponent_alliance, [])
            team_data_from_opponents = {
                'rankCounterDefense': [],
                'rankResistance': [],
            }
            for opponent_team in opponent_data:
                team_data = opponent_team['opponents']
                team_data = [team2 for team2 in team_data if \
                    team2['teamNumber'] == team_number][0]
                for key, value_list in team_data_from_opponents.items():
                    value_list.append(team_data[key])
            for key, value_list_ in team_data_from_opponents.items():
                temp_super_teams[team_number][key] = avg_without_zeroes(value_list_)

    for team_number, data in temp_super_teams.items():
        timd_name = f'{team_number}Q{match_number}'
        for folder in ['cache', 'upload_queue']:
            try:
                with open(f'data/{folder}/timds/{timd_name}.json', 'r') as file:
                    file_data = json.load(file)
            except FileNotFoundError:
                file_data = {}
            file_data.update(data)
            with open(f'data/{folder}/timds/{timd_name}.json', 'w') as file:
                json.dump(file_data, file)
