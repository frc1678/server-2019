"""Calculations for a single TIMD.

TIMD stands for Team In Match Data.  TIMD calculations include
consolidation of (up to) 3 tempTIMDs (temporary TIMDs) into a single
TIMD, and the calculation of data points that are reflective of a team's
performance in a single match.

Consolidation is the process of determining the actions a robot
performed in a match by using data from (up to) 3 tempTIMDs.  One
tempTIMD is created per scout per match.  Ideally, 18 scouts are
distributed evenly across the 6 robots per match, resulting in 3
tempTIMDs per robot per match (aka 3 tempTIMDs per TIMD).  However, the
number of tempTIMDs per TIMD may be less than 3, depending on scout
availability, incorrect scout distribution, or missing data.

Called by server.py with the name of the TIMD to be calculated."""
#!/usr/bin/python3.7
# External imports
import json
import sys
# Internal imports
import utils
'''
# Check to ensure TIMD name is being passed as an argument
if len(sys.argv) == 2:
    # Extract TIMD name from system argument
    TIMD_NAME = sys.argv[1]
else:
    print('Error: TIMD name not being passed as an argument. Exiting...')
    sys.exit(0)
'''
TIMD_NAME = 't'
#TODO: Open tempTIMD data

#TODO: Add decompression to decompress timds before they are calculated

# CONSOLIDATION OF TEMPTIMDS

#TODO: Add implementation for TEMP_TIMDS and sprking
SPRKING = 'h'
TEMP_TIMDS = {'h' : {
    'startingLevel': 2,
    'crossedHabLine': True,
    'startingLocation': 'left',
    'preload' : 'lemon',
    'driverStation': 1,
    'isNoShow': False,
    'timerStarted': 1547528330,
    'currentCycle': 4,
    'scoutID': 7,
    'scoutName': 'Carl',
    'appVersion': '1.2',
    'assignmentMode': 'QR',
    'assignmentFileTimestamp': 1547528290,
    'matchesNotScouted': [1, 14, 28, 35],
    'timeline': [
        {
            'type': 'intake',
            'time' : '102.4',
            'piece': 'orange',
            'zone': 'rightLoadingStation',
            'didSucceed': True,
            'wasDefended': False,
        },
        {
            'type': 'incap',
            'time': '109.6',
            'cause': 'brokenMechanism',
        },
        {
            'type': 'unincap',
            'time': '111.1',
        },
        {
            'type': 'drop',
            'time': '112.1',
            'piece': 'orange',
        },
        {
            'type': 'intake',
            'time': '120',
            'piece': 'lemon',
            'zone': 'zone2Left',
            'didSucceed': True,
            'wasDefended': True,
        },
        {
            'type': 'placement',
            'time': '127.4',
            'piece': 'lemon',
            'didSucceed': False,
            'wasDefended': False,
            'structure': 'leftRocket',
            'side': 'right',
            'level': 2,
        },
        {
            'type': 'spill',
            'time': '130',
            'piece': 'lemon',
        },
        {
            'type': 'climb',
            'time': '138',
            'attempted': {'self': 3, 'robot1': 3, 'robot2': 2},
            'actual': {'self': 3, 'robot1': 2, 'robot2': 1},
        }
    ],
}, 'r' : {
    'startingLevel': 1,
    'crossedHabLine': None,
    'startingLocation': 'mid',
    'preload' : 'lemon',
    'driverStation': 1,
    'isNoShow': False,
    'timerStarted': 1547528330,
    'currentCycle': 4,
    'scoutID': 7,
    'scoutName': 'Carl',
    'appVersion': '1.2',
    'assignmentMode': 'QR',
    'assignmentFileTimestamp': 1547528290,
    'matchesNotScouted': [1, 14, 28, 35],
    'timeline': [
        {
            'type': 'intake',
            'time' : '102.4',
            'piece': 'orange',
            'zone': 'rightLoadingStation',
            'didSucceed': True,
            'wasDefended': False,
        },
        {
            'type': 'incap',
            'time': '109.6',
            'cause': 'brokenMechanism',
        },
        {
            'type': 'unincap',
            'time': '111.1',
        },
        {
            'type': 'drop',
            'time': '112.1',
            'piece': 'orange',
        },
        {
            'type': 'intake',
            'time': '120',
            'piece': 'lemon',
            'zone': 'zone2Left',
            'didSucceed': True,
            'wasDefended': True,
        },
        {
            'type': 'placement',
            'time': '127.4',
            'piece': 'lemon',
            'didSucceed': False,
            'wasDefended': False,
            'structure': 'leftRocket',
            'side': 'right',
            'level': 2,
        },
        {
            'type': 'spill',
            'time': '130',
            'piece': 'lemon',
        },
        {
            'type': 'climb',
            'time': '138',
            'attempted': {'self': 3, 'robot1': 3, 'robot2': 2},
            'actual': {'self': 3, 'robot1': 2, 'robot2': 1},
        }
    ],
}, 'g' : {
    'startingLevel': 3,
    'crossedHabLine': None,
    'startingLocation': 'left',
    'preload' : 'lemon',
    'driverStation': 1,
    'isNoShow': False,
    'timerStarted': 1547528330,
    'currentCycle': 4,
    'scoutID': 7,
    'scoutName': 'Carl',
    'appVersion': '1.2',
    'assignmentMode': 'QR',
    'assignmentFileTimestamp': 1547528290,
    'matchesNotScouted': [1, 14, 28, 35],
    'timeline': [
        {
            'type': 'intake',
            'time' : '102.4',
            'piece': 'orange',
            'zone': 'rightLoadingStation',
            'didSucceed': True,
            'wasDefended': False,
        },
        {
            'type': 'incap',
            'time': '109.6',
            'cause': 'brokenMechanism',
        },
        {
            'type': 'unincap',
            'time': '111.1',
        },
        {
            'type': 'drop',
            'time': '112.1',
            'piece': 'orange',
        },
        {
            'type': 'intake',
            'time': '120',
            'piece': 'lemon',
            'zone': 'zone2Left',
            'didSucceed': True,
            'wasDefended': True,
        },
        {
            'type': 'placement',
            'time': '127.4',
            'piece': 'lemon',
            'didSucceed': False,
            'wasDefended': False,
            'structure': 'leftRocket',
            'side': 'right',
            'level': 2,
        },
        {
            'type': 'spill',
            'time': '130',
            'piece': 'lemon',
        },
        {
            'type': 'climb',
            'time': '138',
            'attempted': {'self': 3, 'robot1': 3, 'robot2': 2},
            'actual': {'self': 3, 'robot1': 2, 'robot2': 1},
        }
    ],
}}

def time_consolidation(times):
    """Takes a certain amount of time options and consolidates them
    using facts and logic. Returns the correct time."""
    

def basic_timeline_consolidation(input_timelines, *types):
    """Takes certain action types out of the timeline and consolidates
    them seperately. Types is an *argv argument which can take in as
    many action types that need to be consolidated together. Returns
    a timeline only made up of action types that were passed as args.
    """

    # The dictionary of three timelines with only the types specified
    # in the function.
    simplified_timelines = {scout : [] for scout in input_timelines.keys()}

    # Takes the three different timelines and cuts out any types of
    # data points which are not the specified types.
    for scout, timeline in input_timelines.items():
        for action in timeline:
            if action.get('type') in types:
                simplified_timelines[scout].append(action)

    #TODO: Create more complex system to consolidate
    # Trusts the simplified timeline of the scout with the best spr
    return simplified_timelines[SPRKING][0]

def climb_consolidation(input_timelines):
    """Takes climb out of the timelines of the tempTIMDs and
    consolidates it. Returns a timeline only with climb inside it
    to add to the final timeline for the timd."""

    # The dictionary of scout name to climb dictionary.
    simplified_timelines = {}

    # Fills in the simplified timelines dictionary with the scout and
    # the climb dictionary from the three tempTIMDs.
    for scout, timeline in input_timelines.items():
        for action in timeline:
            if action.get('type') == 'climb':
                simplified_timelines[scout] = action

    #TODO: Create more complex system to consolidate
    return simplified_timelines[SPRKING]

FINAL_TIMD = {}

# When consolidating non-timed keys, it is easy to consolidate them,
# as you can simply find which value is the most common in the set of
# three possibilities.

# Iterates through the keys of the first tempTIMD and finds the ones
# that are not timed or scout diagnostics.
for data_field in list(TEMP_TIMDS[SPRKING]):
    if data_field not in ['timeline',
                          'timerStarted',
                          'currentCycle',
                          'scoutID',
                          'scoutName',
                          'appVersion',
                          'assignmentMode',
                          'assignmentFileTimestamp',
                          'matchesNotScouted']:

        # Creates a dictionary of each scout to the key from their
        # tempTIMD to compare against each other. (Code note - This code
        # is using .get and not simply referencing the key out of the
        # dictionary because .get doesn't error out when the key doesn't
        # exist. It instead returns NoneType).
        data_field_comparison_list = {scout : dicti.get(data_field) for scout, dicti in
                                      TEMP_TIMDS.items() if dicti.get(data_field) is not None}

        # If there are NoneTypes in the list, truncnate them, they mess
        # up later calculation. However, if they all are None, the data
        # point is missing,
        # Creates a dictionary with how many times an item appeared in
        # the comparison list.
        occurence_list = {data_field : list(data_field_comparison_list.values()).count(data_field)
                          for data_field in set(data_field_comparison_list.values())}

        # If the highest occurence on the occurence list is the same as
        # the lowest occurence, the correct value for the datapoint is
        # the value output by the scout with the best spr. This triggers
        # both when all the scout values are the same (The max and min
        # would both be three) and when all the scout values are
        # different (The max and min are both 1). In the case of any
        # other scenario, the max is trusted because it would suggest
        # the max is the 2 in a 2 scout versus 1 split decision.
        if max(occurence_list.values()) == min(occurence_list.values()):
            FINAL_TIMD[data_field] = TEMP_TIMDS[SPRKING][data_field]
        else:
            FINAL_TIMD[data_field] = max(occurence_list, key=occurence_list.get)
    # If the data field name is not any of the non-timed data keys or
    # the timeline (Which is computed later) it shouldn't be
    # consolidated. This group of data fields in the tempTIMDs is
    # mostly scout diagnostics.
    elif data_field != 'timeline':
        pass
    # If the data field doesn't fit any of the previous requirements,
    # it must be the timeline.
    else:
        # In order to compute the timeline properly, it is split into
        # a list of the timelines.
        timelines = {scout : temp_timd.get('timeline') for
                     scout, temp_timd in TEMP_TIMDS.items()
                     if temp_timd.get('timeline') is not None}

        # If the list of timelines only includes one timeline, that
        # timeline is taken as the correct one and put into the final
        # TIMD.
        if len(timelines.values()) == 1:
            FINAL_TIMD['timeline'] = timelines[SPRKING]
        #TODO: Program case of 2 tempTIMDs

        # If the list has three tempTIMDs, the process for computation
        # is more complicated.
        else:
            # Creates the final timeline which is passed as the
            # timeline for the final timd at the end of consolidation.
            final_timeline = []

            # Before the hard part of consolidating intakes and
            # placements comes in, it seperates other types of actions
            # that aren't necessary to be consolidated with them and
            # passes them as arguments to the basic consolidation
            # function.
            final_timeline.append(basic_timeline_consolidation(timelines, 'spill'))
            final_timeline.append(basic_timeline_consolidation(timelines, 'incap', 'unincap'))
            final_timeline.append(basic_timeline_consolidation(timelines, 'drop'))

            # Also consolidates climb seperately in order to seperate it
            # from intakes and placements.
            final_timeline.append(climb_consolidation(timelines))
            print(final_timeline)






'''



# Save data in local cache
with open(utils.create_file_path('data/timds/' + TIMD_NAME + '.json'),
          'w') as file:
    json.dump(FINAL_TIMD, file)

# Save data in Firebase upload queue
with open(utils.create_file_path('data/upload_queue/timds' + TIMD_NAME +
                                 '.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)
'''