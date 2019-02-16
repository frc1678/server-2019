#!/usr/bin/python3.6
"""Creates and sends Scout assignment file."""
# External imports
import json
import string
import time
# Internal imports
import tba_communicator
import utils

def create_assignment_file(matches, scout_names):
    """Creates scout assignment file."""
    teams_by_match = {}
    for match_data in matches:
        # 'qm' stands for qualification match
        if match_data['comp_level'] == 'qm':
            red_teams = match_data['alliances']['red']['team_keys']
            blue_teams = match_data['alliances']['blue']['team_keys']
            match_number = match_data['match_number']
            # Remove 'frc' from team number and convert to integer
            # (e.g. 'frc1678' -> 1678)
            red_teams = [int(team[3:]) for team in red_teams]
            blue_teams = [int(team[3:]) for team in blue_teams]
            teams = []
            for team in red_teams:
                teams.append({'number': team, 'alliance': 'red'})
            for team in blue_teams:
                teams.append({'number': team, 'alliance': 'blue'})
            teams_by_match[match_number] = {index: team for index,
                                            team in enumerate(teams, 1)}

    scout_name_compression_letters = {}
    # 'string.ascii_letters' contains letters a-z and A-Z
    letters = list(string.ascii_letters)
    for index in range(len(scout_names)):
        scout_name_compression_letters[scout_names[index]] = letters[index]

    return {
        'matches': teams_by_match,
        'letters': scout_name_compression_letters,
        'timestamp': time.time(),
    }


SCOUT_NAMES = [
    'Sam C', 'Sam S', 'Carl', 'Ethan', 'John', 'Jack', 'Bob', 'Joe',
    'Example', 'Running', 'Out', 'Of', 'Names', 'To', 'Use',
    # '.zfill(2)' adds leading zeroes to 2 decimal places
    # (e.g. '7' becomes '07')
    # Used by the Scout app to alphabetize scout names
] + [f'Backup {str(n).zfill(2)}' for n in range(1, 10+1)]

MATCHES = tba_communicator.request_matches()
ASSIGNMENT_FILE = create_assignment_file(MATCHES, SCOUT_NAMES)

with open(utils.create_file_path('data/assignments/assignments.json', True), 'w') as file:
    json.dump(ASSIGNMENT_FILE, file)

with open(utils.create_file_path('data/assignments/assignments.txt', True), 'w') as file:
    # 'json.dumps()' returns a JSON string
    file.write(json.dumps(ASSIGNMENT_FILE))
