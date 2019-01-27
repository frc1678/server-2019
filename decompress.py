"""Timeline tempTIMD decompression.

Creates timeline_decompression function, takes in the compressed tempTIMD as a string then
decompresses and formats it to make the complete decompressed timeline for tempTIMD."""
import string

def timeline_decompression(compressed_tempTIMD):
    """Decompresses tempTIMD timeline.

    Converts the compressed tempTIMD to the to a decompressed list of dictionaries representing each
    action in the timeline."""
    # Dictionaries with the compressed item as the key and the decompressed item as the value
    compresskey = {
        'a': 'startingLevel',
        'b': 'crossedHabLine',
        'c': 'startingLocation',
        'd': 'preload',
        'e': 'driverStation',
        'f': 'isNOShow',
        'g': 'timerStarted',
        'h': 'currentCycle',
        'j': 'scoutID',
        'k': 'scoutName',
        'm': 'appVersion',
        'n': 'appVersion',
        'p': 'assignmentFileTimeStamp',
        'q': 'matchesNotScouted',
        'r': 'type',
        's': 'time',
        't': 'piece',
        'u': 'zone',
        'v': 'didSucceed',
        'w': 'wasDefended',
        'x': 'structure',
        'y': 'side',
        'z': 'level',
        'A': 'cause',
        'B': 'attempted',
        'C': 'actual',
        'D': 'self',
        'E': 'robot1',
        'F': 'robot2'
    }
    compressvalue = {
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
    }
    # Splits the compressed tempTIMD, separating the team, scout, and header from the time-line
    # Then splits the actions
    compressed_timeline = compressed_tempTIMD.split('_')[1].split(',')
    # List for each of the dictionaries for each action to be put into
    decompressed_data = []
    # Will be set to a new number every time iteration encounters a key
    index_last_key = 0
    # Will change when iteration encounters an open curly-bracket
    inside_curly_bracket = False
    for action in compressed_timeline:
        # Creates a dictionary for each action in the timeline
        action_dic = {}
        # Cycles through the details for each action and assigns index
        for index, char in enumerate(action):
            # Checks to see if iteration found a curly-bracket
            # Knows that it is looking inside the curly-brackets
            if char == '{':
                inside_curly_bracket = True
            # Knows it is no longer looking at characters in the curly-brackets
            elif char == '}':
                inside_curly_bracket = False
            # Checks to see if iteration is inside curly-brackets
            elif inside_curly_bracket is True:
                # There must be a key before the curly-brackets
                # Checks to see of there is already a value for the key
                climb_detail = action_dic.get(compresskey[key], '')
                # Adds the new character to the previous character as part of the value
                value = climb_detail + char
                # Decompresses key using the compresskey dictionary
                # Adds the key and complete decompressed climb data to the dictionary for the action
                action_dic[compresskey[key]] = value
            # Checks if the character is a letter
            elif char in string.ascii_letters:
                # Checks to see if the character is not the first item
                # Because index_last_key is defined later in the if statement the index of the
                # current character minus index of the previous character means that the previous
                # character is the key and the current character is the value.
                if index - index_last_key == 1:
                    # Sets the letter character that must be a value to a variable
                    value = char
                    # Decompresses keys and values using compresskey and compressvalue dictionaries
                    # Adds the previous character as the key and the current character as the value
                    action_dic[compresskey[key]] = compressvalue[value]
                else:
                    # This character must be a key because it is not a value
                    # Sets index of the key to index_last_key that will be used when finding value
                    index_last_key = index
                    key = char
            else:
                # Because the character is a number then there must already be a key before it
                # Checks to see if there is already a value for the key, sets to variable
                number_value = action_dic.get(compresskey[key], '')
                # Adds the value already set to the key to the new character that is also a number
                value = number_value + char
                # Decompresses the key and adds the value to the dictionary for the action
                action_dic[compresskey[key]] = value
        # Special case to deal with the data from the climb
        # Finds what action dictionary has climb in it
        if 'climb' in action_dic.values():
            for climb_key, data in action_dic.items():
                # Creates a dictionary for the attempted and actual climb data
                climb_dic = {}
                if climb_key in ('attempted', 'actual'):
                    # If the key is 'attempted' or 'actual', splits the value between the robots
                    semi_split_climb = action_dic[climb_key].split(';')
                    for climb_info in semi_split_climb:
                        # Splits each climb between the robot and the climb levels
                        climb_list = climb_info.split(':')
                        # Adds the first item in the list as the key and the second as the value
                        climb_dic[compresskey[climb_list[0]]] = int(climb_list[1])
                    # Adds the climb dictionaries to the values of 'actual' and 'attempted'
                    action_dic[climb_key] = climb_dic
        # Adds each action to a list that makes up the complete timeline
        decompressed_data.append(action_dic)
