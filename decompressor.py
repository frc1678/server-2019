"""Decompresses tempTIMD data.

Called by calculate_timd.py."""
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
    'n': 'stuchOnHab',
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
    decompressed_temp_timd['timeline'] = decompress_temp_timd_timeline(
        compressed_timeline)

    return {temp_timd_key: decompressed_temp_timd}
