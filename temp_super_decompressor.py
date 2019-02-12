"""Decompresses tempSuper data.

Called by forward_temp_super.py"""

# Compressed tempSuper key to uncompressed tempSuper key
TEMP_SUPER_COMPRESSION_KEYS = {
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
                decompressed_preload_key = TEMP_SUPER_COMPRESSION_VALUES[
                    compressed_preload_key]
                decompressed_preload_value = TEMP_SUPER_COMPRESSION_VALUES[
                    compressed_preload_value]
                decompressed_value[decompressed_preload_key] = \
                    decompressed_preload_value
        elif decompressed_key == 'noShowTeams':
            # 'noShowTeams' is a list
            # Removes 'compressed_key' and brackets
            teams = header[2:-1]
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
            # Checks if the value is a letter that can be decompressed.
            if compressed_value in TEMP_SUPER_COMPRESSION_VALUES:
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
    teamSuper teams data contians data that is specific to a team.

    compressed_temp_super is a string."""
    compressed_header = compressed_temp_super.split('_')[0]
    compressed_team = compressed_temp_super.split('_')[1]

    decompressed_temp_super = {}

    decompressed_temp_super.update(decompress_temp_super_headers(
        compressed_header))
    decompressed_temp_super.update(decompress_temp_super_teams(
        compressed_team))

    return decompressed_temp_super
