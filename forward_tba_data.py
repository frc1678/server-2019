#!/usr/bin/python3.6
"""Forwards data from TBA (The Blue Alliance) to Teams, TIMDs, and Matches.

Called by server.py"""
# External imports
import json
# Internal imports
import tba_communicator
import utils

def update_json_file(file_path, updated_data):
    """Updates data in a JSON file.  (Preserves old data)

    file_path is the absolute path of the file to be updated (string)
    updated_data is the data to add to the JSON file (dict)"""
    try:
        with open(file_path, 'r') as file:
            file_data = json.load(file)
    except FileNotFoundError:
        file_data = {}
    # Used for nested dictionaries (i.e. 'calculatedData')
    for key, value in updated_data.items():
        if isinstance(value, dict):
            file_data[key] = file_data.get(key, {})
            file_data[key].update(value)
        else:
            file_data[key] = value
    with open(file_path, 'w') as file:
        json.dump(file_data, file)

def save_data(file_path, data):
    """Saves data in 'cache' and 'upload_queue' directories.

    file_path is the relative file path to a JSON file from inside the
    'cache' or 'upload_queue' folder. (string)
    data is a dictionary that the JSON file is updated with."""
    # Removes preceding slash
    if file_path[0] == '/':
        file_path = file_path[1:]
    update_json_file(utils.create_file_path(f'data/cache/{file_path}'), data)
    update_json_file(utils.create_file_path(
        f'data/upload_queue/{file_path}'), data)


# Team data
RANKINGS = tba_communicator.request_rankings()['rankings']
for team in RANKINGS:
    # Removes preceding 'frc'
    # (e.g. 'frc1678' becomes '1678')
    team_number = team['team_key'][3:]
    team_data = {
        'actualRPs': team['extra_stats'][0],
        'matchesPlayed': team['matches_played'],
        # TODO: Move actual seed into non-calculated match data
        'calculatedData': {
            'actualSeed': team['rank'],
        },
    }
    save_data(f'teams/{team_number}.json', team_data)

# TIMD and Match data
MATCH_KEYS = tba_communicator.request_match_keys()
# Match key to match data
MATCH_DATA = {}
print('Retrieving all match data from TBA...')
for match_key in MATCH_KEYS:
    # 'qm' stands for qualification match
    # Example 'match_key' formats: '2019caoc_qm29', '2019caoc_qf3m1'
    if match_key.split('_')[1][:2] == 'qm':
        match = tba_communicator.request_match(match_key, show_output=False, acceptable_cache_age=60)
        MATCH_DATA[match_key] = match
print('All TBA match data successfully retrieved.')

for match_key, match in MATCH_DATA.items():
    match_number = match['match_number']
    teams_by_alliance = {
        'red': match['alliances']['red']['team_keys'],
        'blue': match['alliances']['blue']['team_keys'],
    }
    # Skip the match if a score_breakdown is not available (meaning the
    # match hasn't been played yet)
    if match.get('score_breakdown') is None:
        continue
    for alliance in teams_by_alliance:
        alliance_score_breakdown = match['score_breakdown'][alliance]
        # Removes preceding 'frc' and casts to int
        # (e.g. 'frc1678' becomes 1678)
        teams = [int(team[3:]) for team in teams_by_alliance[alliance]]
        no_show_teams = []
        # 'teams' are ordered by driver station
        # (e.g. for [1678, 3132, 1323]; 1678 is driver station 1, 3132
        # is driver station 2, and 1323 is driver station 3)

        # TIMD data
        for driver_station, team_number in enumerate(teams, 1):
            starting_level = alliance_score_breakdown[
                f'preMatchLevelRobot{driver_station}']
            # Decompresses 'starting_level'
            decompression = {
                'HabLevel1': 1,
                'HabLevel2': 2,
                'None': None,
                'Unknown': None,
            }
            starting_level = decompression[starting_level]
            # Checks if team is a no-show
            if starting_level is None:
                no_show_teams.append(team_number)
                is_no_show = True
                # 'hab_line_crossed' cannot exist if the team is a no-show.
                hab_line_crossed = None
            else:
                is_no_show = False
                hab_line_crossed = alliance_score_breakdown[
                    f'habLineRobot{driver_station}']
                # Converts 'hab_line_crossed' to boolean
                if hab_line_crossed == 'CrossedHabLineInSandstorm':
                    hab_line_crossed = True
                else:
                    hab_line_crossed = False
            timd_data = {
                'driverStation': driver_station,
                'startingLevel': starting_level,
                'isNoShow': is_no_show,
                'crossedHabLine': hab_line_crossed,
            }
            # Example TIMD name: '1678Q3' (1678 in match 3)
            timd_name = f'{team_number}Q{match_number}'
            save_data(f'timds/{timd_name}.json', timd_data)

        # Match data
        actual_score = alliance_score_breakdown['totalPoints']
        foul_points = alliance_score_breakdown['foulPoints']
        rocket_rp = alliance_score_breakdown['completeRocketRankingPoint']
        climb_rp = alliance_score_breakdown['habDockingRankingPoint']
        total_rps = alliance_score_breakdown['rp']
        # TODO: Add cargo ship preload (requires position of
        # scorekeeping table)
        match_data = {
            f'{alliance}ActualScore': actual_score,
            f'{alliance}FoulPoints': foul_points,
            f'{alliance}DidRocketRP': rocket_rp,
            f'{alliance}DidClimbRP': climb_rp,
            # TODO: Move actual RPs into non-calculated match data
            'calculatedData': {
                f'{alliance}ActualRPs': total_rps,
            }
        }
        save_data(f'matches/{match_number}.json', match_data)
