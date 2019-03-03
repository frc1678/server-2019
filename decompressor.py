"""Decompresses tempTIMD and tempSuper data.

Called by calculate_timd.py or forward_temp_super.py."""
# External imports
import json
# Internal imports
import utils

# Compressed tempTIMD key to uncompressed tempTIMD key
TEMP_TIMD_COMPRESSION_KEYS = {
    'a': 'startingLevel',
    'b': 'crossedHabLine',
    'c': 'startingLocation',
    'd': 'preload',
    'e': 'driverStation',
    'f': 'isNoShow',
    'g': 'timerStarted',
    'h': 'currentCycle',
    'j': 'scoutID',
    'k': 'scoutName',
    'm': 'appVersion',
    'n': 'assignmentMode',
    'p': 'assignmentFileTimestamp',
    'G': 'sandstormEndPosition',
    'r': 'type',
    's': 'time',
    't': 'piece',
    'u': 'zone',
    'v': 'didSucceed',
    'w': 'wasDefended',
    'H': 'shotOutOfField',
    'x': 'structure',
    'y': 'side',
    'z': 'level',
    'A': 'cause',
    'B': 'attempted',
    'C': 'actual',
    'D': 'self',
    'E': 'robot1',
    'F': 'robot2',
}
# Compressed tempTIMD value to uncompressed tempTIMD value
TEMP_TIMD_COMPRESSION_VALUES = {
    'T': True,
    'F': False,
    'A': 'left',
    'B': 'mid',
    'C': 'right',
    'D': 'far',
    'E': 'orange',
    'G': 'lemon',
    'H': 'none',
    'J': 'QR',
    'K': 'backup',
    'L': 'override',
    'M': 'intake',
    'N': 'placement',
    'P': 'drop',
    'Q': 'spill',
    'R': 'climb',
    'S': 'incap',
    'U': 'unincap',
    't': 'startDefense',
    'u': 'endDefense',
    'V': 'zone1Left',
    'W': 'zone1Right',
    'X': 'zone2Left',
    'Y': 'zone2Right',
    'Z': 'zone3Left',
    'a': 'zone3Right',
    'b': 'zone4Left',
    'c': 'zone4Right',
    'd': 'leftLoadingStation',
    'e': 'rightLoadingStation',
    'f': 'leftRocket',
    'g': 'rightRocket',
    'h': 'cargoShip',
    'j': 'tippedOver',
    'k': 'brokenMechanism',
    'm': 'stuckOnObject',
    'n': 'stuckOnHab',
    'p': 'emergencyStop',
    'q': 'noControl',
    'r': 'twoGamePieces',
    's': 'near',
}

def decompress_temp_timd_value(compressed_value):
    """Decompresses a single tempTIMD value.

    compressed_value is a string."""
    # If the 'compressed_value' is a one-character letter, it needs to
    # be decompressed.
    if len(compressed_value) == 1 and compressed_value.isalpha():
        return TEMP_TIMD_COMPRESSION_VALUES[compressed_value]
    # Checks if 'compressed_value' only contains characters 0-9
    elif compressed_value.isdigit():
        # 'compressed_value' is an integer
        return int(compressed_value)
    # Otherwise, 'compressed_value' should be left as a string, since it
    # is a timestamp (which can contain '*' characters), an app version,
    # or a climb dictionary (which is handled later).
    else:
        return compressed_value

def decompress_temp_timd_headers(compressed_headers):
    """Decompress headers for a single tempTIMD.

    compressed_headers are non-timed data fields."""

    with open(utils.create_file_path(
            'data/assignments/assignments.json'), 'r') as file:
        file_data = json.load(file)
    # Decompressed scout name to compressed scout name
    scout_name_compression_values = file_data['letters']

    # Reverses key:value pairs to enable accessing decompressed scout
    # name from compressed scout name
    scout_name_compression_values = {letter: scout_name for \
        scout_name, letter in scout_name_compression_values.items()}

    if compressed_headers[-1] == ',':
        # Removes trailing comma.
        compressed_headers = compressed_headers[:-1]

    compressed_headers = compressed_headers.split(',')

    decompressed_headers = {}

    for header in compressed_headers:
        compressed_key = header[0]
        compressed_value = header[1:]
        decompressed_key = TEMP_TIMD_COMPRESSION_KEYS[compressed_key]
        if decompressed_key == 'scoutName':
            # Uses 'scout_name_compression_values' dictionary to decompress scout name
            decompressed_value = scout_name_compression_values[compressed_value]
        else:
            decompressed_value = decompress_temp_timd_value(compressed_value)
        decompressed_headers[decompressed_key] = decompressed_value

    return decompressed_headers

def decompress_temp_timd_timeline(compressed_temp_timd_timeline):
    """Decompresses a single tempTIMD timeline.

    Decompresses a tempTIMD timeline to a list of dictionaries.
    Each dictionary represents an action in the timeline.

    compressed_temp_timd_timeline is a string."""
    if compressed_temp_timd_timeline[-1] == ',':
        # In case of an extra comma in the headers it removes them
        compressed_temp_timd_timeline = compressed_temp_timd_timeline[:-1]
    compressed_temp_timd_timeline = compressed_temp_timd_timeline.split(',')
    decompressed_timeline = []
    for action in compressed_temp_timd_timeline:
        decompressed_action = {}
        # Index of the last key in the action.
        index_last_key = 0
        inside_curly_bracket = False

        for index, character in enumerate(action):
            if character == '{':
                inside_curly_bracket = True
            elif character == '}':
                inside_curly_bracket = False
            if inside_curly_bracket is True:
                # Ignore characters in curly brackets (e.g. climb), and
                # deal with them later.
                pass
            # The character is the last character in the string
            elif index == len(action)-1:
                # Decompress the previous key and value
                decompressed_key = TEMP_TIMD_COMPRESSION_KEYS[key]
                # The previous value is from the last key to the end of
                # the string.
                compressed_value = action[index_last_key+1:]
                decompressed_value = decompress_temp_timd_value(
                    compressed_value)

                # Save the previous key:value pair in the final dictionary.
                decompressed_action[decompressed_key] = decompressed_value
            # Special handling for the first key
            elif character.isalpha() and index == 0:
                index_last_key = 0
                key = character
            # The character is a key if it is more than one character
            # after the last key and it is a letter.
            elif character.isalpha() and (index - index_last_key > 1):
                # Decompress the previous key and value
                decompressed_key = TEMP_TIMD_COMPRESSION_KEYS[key]
                # The previous value is between the last key and the
                # current key.
                compressed_value = action[index_last_key+1:index]
                decompressed_value = decompress_temp_timd_value(
                    compressed_value)

                # Save the previous key:value pair in the final dictionary.
                decompressed_action[decompressed_key] = decompressed_value

                # Save the index and value of the key
                index_last_key = index
                key = character

        # Special case to deal with the data from the climb.
        # Finds which action dictionary has climb in it.
        if decompressed_action.get('type') == 'climb':
            for climb_key in ['attempted', 'actual']:
                # 'climb_items' example format: ['D3', 'E3', 'F0']
                # [1:-1] removes curly brackets
                climb_items = decompressed_action[climb_key][1:-1].split(';')
                decompressed_climb = {}
                for climb_item in climb_items:
                    compressed_key = climb_item[0]
                    compressed_value = climb_item[1]
                    decompressed_key = TEMP_TIMD_COMPRESSION_KEYS[
                        compressed_key]
                    decompressed_value = int(compressed_value)
                    decompressed_climb[decompressed_key] = decompressed_value
                decompressed_action[climb_key] = decompressed_climb

        decompressed_timeline.append(decompressed_action)
    return decompressed_timeline

def decompress_temp_timd(compressed_temp_timd):
    """Decompresses a single tempTIMD.

    Calls decompress_temp_timd_headers() and
    decompress_temp_timd_timeline().
    The headers are the non-timed data fields and are stored in a
    dictionary.  The timeline is a list of dictionaries.  Each
    dictionary represents a timed action.  Returns a dictionary.

    compressed_temp_timd is a string."""
    temp_timd_key = compressed_temp_timd.split('|')[0]
    compressed_header = compressed_temp_timd.split('|')[1].split('_')[0]
    compressed_timeline = compressed_temp_timd.split('_')[1]

    decompressed_temp_timd = {}

    decompressed_temp_timd.update(decompress_temp_timd_headers(
        compressed_header))
    # If 'compressed_timeline' is empty, it cannot be decompressed.
    # This occurs if a team is a no-show, or if they do not perform any
    # actions during the match.
    if compressed_timeline != '':
        decompressed_temp_timd['timeline'] = decompress_temp_timd_timeline(
            compressed_timeline)
    return {temp_timd_key: decompressed_temp_timd}



# Compressed tempSuper key to uncompressed tempSuper key
TEMP_SUPER_COMPRESSION_KEYS = {
    'a': 'cargoShipPreloads',
    'b': 'leftNear',
    'c': 'leftMid',
    'd': 'leftFar',
    'e': 'rightNear',
    'f': 'rightMid',
    'g': 'rightFar',
    'h': 'noShowTeams',
    'k': 'redScore',
    'm': 'blueScore',
    'n': 'redFoulPoints',
    'p': 'blueFoulPoints',
    'q': 'blueDidRocketRP',
    'r': 'redDidRocketRP',
    's': 'blueDidClimbRP',
    't': 'redDidClimbRP',
    'u': 'teamNumber',
    'v': 'rankAgility',
    'w': 'rankSpeed',
    'x': 'rankDefense',
    'y': 'rankCounterDefense',
    'z': 'notes',
    '1': 'team1',
    '2': 'team2',
    '3': 'team3',
    'A': 'numGoodDecisions',
    'B': 'numBadDecisions',
    'j': 'wasHitDuringSandstorm',
}
# Compressed tempSuper value to uncompressed tempSuper value
TEMP_SUPER_COMPRESSION_VALUES = {
    'T': True,
    'F': False,
    'B': 'blue',
    'R': 'red',
    'G': 'orange',
    'L': 'lemon',
}

def decompress_temp_super_headers(compressed_temp_super_headers):
    """Decompresses headers for a single tempSuper.

    Headers contain the data that is not specific to a team."""
    compressed_temp_super_headers = compressed_temp_super_headers.split(',')
    decompressed_super = {}
    for header in compressed_temp_super_headers:
        compressed_key = header[0]
        compressed_value = header[1:]
        decompressed_key = TEMP_SUPER_COMPRESSION_KEYS[compressed_key]

        if decompressed_key == 'cargoShipPreloads':
            # Removes 'compressed_key' and curly brackets
            compressed_value = header[2:-1]

            decompressed_value = {}
            for compressed_preload in compressed_value.split(';'):
                compressed_preload_key = compressed_preload[0]
                compressed_preload_value = compressed_preload[1:]
                decompressed_preload_key = TEMP_SUPER_COMPRESSION_KEYS[
                    compressed_preload_key]
                decompressed_preload_value = TEMP_SUPER_COMPRESSION_VALUES[
                    compressed_preload_value]
                decompressed_value[decompressed_preload_key] = \
                    decompressed_preload_value
        elif decompressed_key == 'noShowTeams':
            # 'noShowTeams' is a list
            # Removes 'compressed_key' and brackets
            teams = header[2:-1]
            # Checks for empty 'noShowTeams'
            if teams == '':
                decompressed_value = []
            else:
                decompressed_value = [int(team) for team in teams.split(';')]
        # Checks if the 'compressed_value' can be decompressed with
        # 'TEMP_SUPER_COMPRESS_VALUES'.
        elif len(compressed_value) == 1 and compressed_value.isalpha():
            decompressed_value = TEMP_SUPER_COMPRESSION_VALUES[
                compressed_value]
        # Checks if 'compressed_value' only contains characters 0-9
        elif compressed_value.isdigit():
            decompressed_value = int(compressed_value)
        else:
            print(f"Error: Unable to process value of '{decompressed_key}': {compressed_value}")
        decompressed_super[decompressed_key] = decompressed_value
    return decompressed_super

def decompress_temp_super_teams(compressed_temp_super_teams):
    """Decompresses a single data set of tempSuper teams.

    Returns a dictionary. Each item in the dictionary represents one of
    the three teams in the tempSuper data.

    compressed_temp_super is a string."""

    # Splits the list of teams at each comma, ignoring commas inside of
    # super notes.  'compressed_teams' is the split list.
    compressed_teams = []
    inside_curly_brackets = False
    last_comma_index = None
    for index, character in enumerate(compressed_temp_super_teams):
        # Checks if the character is the last character.
        if index == len(compressed_temp_super_teams)-1:
            # Adds all characters after the last comma to 'teams'
            compressed_teams.append(compressed_temp_super_teams[last_comma_index+1:])
        # Ignore commas inside team dictionaries (surrounded with curly
        # brackets)
        if character == '{':
            inside_curly_brackets = True
        elif character == '}':
            inside_curly_brackets = False
        elif inside_curly_brackets is False and character == ',':
            # This comma separates two team dictionaries, and we should
            # split at this character.
            if last_comma_index is None:
                # Adds all characters before the first comma to 'compressed_teams'
                compressed_teams.append(compressed_temp_super_teams[:index])
            else:
                # Adds all characters between the previous comma and
                # current comma to 'compressed_teams'
                compressed_teams.append(compressed_temp_super_teams[last_comma_index+1:index])
            last_comma_index = index

    decompressed_teams = {}
    for team in compressed_teams:
        compressed_team_key = team[0]
        decompressed_team_key = TEMP_SUPER_COMPRESSION_KEYS[compressed_team_key]
        # 'decompressed_team_value' contains
        # 'decompressed_key':'decompressed_value' pairs
        decompressed_team_value = {}
        # Separates each team data item (key:value pair).
        # [2:-1] removes the 'compressed_key' and the curly brackets
        #
        # 'team_items' are compressed key:value pairs for a single team
        team_items = team[2:-1].split(';')
        for team_item in team_items:
            # The first character in the team data will always be the key.
            compressed_key = team_item[0]
            decompressed_key = TEMP_SUPER_COMPRESSION_KEYS[compressed_key]
            # Every character after the key is the value.
            compressed_value = team_item[1:]
            if compressed_key == 'x':
                compressed_value = compressed_value[1:-1]
                for rank_defense in compressed_value:
                    if isalpha(rank_defense) == True:
                        rank_defense_key = TEMP_SUPER_COMPRESSION_KEYS[rank_defense]
                    elif isdigit(rank_defense) == True:
                        rank_defense_value = int(rank_defense)


            # Checks if the value is a letter that can be decompressed.
            elif compressed_value in TEMP_SUPER_COMPRESSION_VALUES:
                # Decompresses the key and the value.
                decompressed_value = TEMP_SUPER_COMPRESSION_VALUES[compressed_value]
            # Checks if the value only contains characters 0-9
            elif compressed_value.isdigit():
                decompressed_value = int(compressed_value)
            else:
                # The value is a super note and should be left as a string.
                decompressed_value = compressed_value
            decompressed_team_value[decompressed_key] = decompressed_value
        # Adds the team data in a dictionary as the value for a team.
        decompressed_teams[decompressed_team_key] = decompressed_team_value
    return decompressed_teams

def decompress_temp_super(compressed_temp_super):
    """Decompresses a single tempSuper data.

    tempSuper headers contain the data that is not specific to a team.
    teamSuper teams data contains data that is specific to a team.

    compressed_temp_super is a string."""
    temp_super_key = compressed_temp_super.split('|')[0]
    compressed_header = compressed_temp_super.split('|')[1].split('_')[0]
    compressed_team = compressed_temp_super.split('_')[1]

    decompressed_temp_super = {}

    decompressed_temp_super.update(decompress_temp_super_headers(
        compressed_header))
    decompressed_temp_super.update(decompress_temp_super_teams(
        compressed_team))

    return {temp_super_key: decompressed_temp_super}
