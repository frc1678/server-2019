import numpy as np

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
            'type': 'startDefense',
            'time': '111.3'
        },
        {
            'type': 'endDefense',
            'time': '111.5'
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
            'time': '131',
            'piece': 'lemon',
        },
        {
            'type': 'spill',
            'time': '135',
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
            'type': 'startDefense',
            'time': '111.3'
        },
        {
            'type': 'endDefense',
            'time': '111.5'
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
            'time': '132',
            'piece': 'lemon',
        },
        {
            'type': 'spill',
            'time': '135',
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
            'type': 'startDefense',
            'time': '111.3'
        },
        {
            'type': 'endDefense',
            'time': '111.5'
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
            'time': '129',
            'piece': 'lemon',
        },
        {
            'type': 'spill',
            'time': '137',
            'piece': 'lemon',
        },
        {
            'type': 'spill',
            'time': '135.2',
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

def max_occurences(comparison_list):
    """Takes in a dictionary of scouts to their input on a certain
    data point. Returns the majority rule, or None if there is no
    clear winner."""

    # If there are NoneTypes in the list, truncnate them, they mess
    # up later calculation. However, if they all are None, the data
    # point is missing,
    # Creates a dictionary with how many times an item appeared in
    # the comparison list.
    occurence_list = {data_field :
                      list(comparison_list.values()).count(data_field)
                      for data_field in set(comparison_list.values())}

    # If the highest occurence on the occurence list is the same as
    # the lowest occurence, the correct value for the datapoint is
    # the value output by the scout with the best spr. This triggers
    # both when all the scout values are the same (The max and min
    # would both be three) and when all the scout values are
    # different (The max and min are both 1). In the case of any
    # other scenario, the max is trusted because it would suggest
    # the max is the 2 in a 2 scout versus 1 split decision.
    if max(occurence_list.values()) == min(occurence_list.values()):
        return comparison_list[SPRKING]
    return max(occurence_list, key=occurence_list.get)

def basic_timeline_consolidation(input_timelines, action_type):
    """Takes an action type out of timelines and consolidates it seperately.

    input_timelines is the dictionary of the scouts to their specific
    timelines. action_type is the action type that the function is
    consolidating. Returns a consolidated timeline only made up of the
    action type that was passed as action_type.
    """

    # The dictionary of three timelines with only the types specified
    # in the function.
    simplified_timelines = {scout : [] for scout in input_timelines.keys()}

    # Takes the three different timelines and cuts out any types of
    # data points which are not the specified types.
    for scout, timeline in input_timelines.items():
        for action in timeline:
            if action.get('type') == action_type:
                simplified_timelines[scout].append(action)

    # Creates a dictionary of scouts to the amount of actions of the
    # specified type are in the timeline.
    count_timelines = {scout : len(timeline) for
                       scout, timeline in simplified_timelines.items()}

    # Finds the majority amount of actions in the timeline to see
    # which amount of actions is the correct amount.
    majority = max_occurences(count_timelines)

    # Creates a dictionary of scouts to their timelines which follow the
    # majority length of timeline.
    correct_length_timelines = {scout : simplified_timelines[scout] for
                                scout, timeline_length in
                                count_timelines.items() if
                                timeline_length == majority}

    # If there are scouts that don't agree with the majority timeline
    time_reference = {scout : [action['time'] for action in timeline]
                      for scout, timeline in
                      correct_length_timelines.items() if scout ==
                      list(correct_length_timelines.keys())[-1]}

    # If there are scouts that do not agree with the correct timeline
    # length, find out which of their action times agree with the time
    # reference the best, and line it up against the reference in the
    # correct_length_timelines dictionary.
    if len(correct_length_timelines.keys()) != len(simplified_timelines.keys()):
        for scout in simplified_timelines.keys():
            if scout not in correct_length_timelines.keys():
                correct_length_timelines[scout] = []
                # In order to find the best option for timings, it sets
                # up a matrix of time differences between each action in
                # each tempTIMD.
                timings = np.zeros((len(simplified_timelines[scout]),
                                    majority))
                for false_index, false_action in \
                        enumerate(simplified_timelines[scout]):
                    for comparison_index, comparison_action in \
                            enumerate(list(time_reference.values())[0]):
                        timings[false_index][comparison_index] = \
                                abs(float(comparison_action) -
                                    float(false_action['time']))

                # Once the matrix of timing differences has been
                # created, the lowest difference is targeted to line up
                # against each other until the entire matrix is deleted.
                while timings[0][0] is not None:
                    print(timings)
                    lowest_index = np.where(timings == timings.min())
                    print(lowest_index)
                    correct_length_timelines[scout] += \
                        simplified_timelines[scout][lowest_index[0][0]]
                    for timing_row in timings:
                        timings = np.delete(timing_row, int(lowest_index[1][0]), 0)
                    timings = np.delete(timings, int(lowest_index[0][0]), 2)
                    print(timings)
                    
                    





    #TODO: Create more complex system to consolidate
    # Trusts the simplified timeline of the scout with the best spr
    return simplified_timelines[SPRKING]

def cycle_consolidation(input_timelines):
    """Takes intakes and placements out of the timelines in the
    tempTIMDs and consolidates them. Returns a timeline only with
    only intakes and placements inside it to add to the final
    timeline for the timd."""

    # The dictionary of three timelines with only intakes and
    # placements.
    simplified_timelines = {scout : [] for scout in input_timelines.keys()}

    # Takes the three different timelines and cuts out any types of
    # data points which are not intakes and placements
    for scout, timeline in input_timelines.items():
        for action in timeline:
            if action.get('type') in ['intake', 'placement', 'drop']:
                simplified_timelines[scout].append(action)

    #TODO: Create more complex system to consolidate
    # Trusts the simplified timeline of the scout with the best spr
    return simplified_timelines[SPRKING]

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
        data_field_comparison_list = {scout : dicti.get(data_field) for
                                      scout, dicti in TEMP_TIMDS.items()
                                      if dicti.get(data_field) is not
                                      None}

        # Uses the max_occurences function to find the correct value 
        # for the data field.
        data_occurence_max = max_occurences(data_field_comparison_list)

        if data_occurence_max is None:
            FINAL_TIMD[data_field] = TEMP_TIMDS[SPRKING][data_field]
        else:
            FINAL_TIMD[data_field] = data_occurence_max
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
            final_timeline += basic_timeline_consolidation(timelines, 'spill')
            final_timeline += basic_timeline_consolidation(timelines, 'incap')
            final_timeline += basic_timeline_consolidation(timelines, 'unincap')
            final_timeline += basic_timeline_consolidation(timelines, 'startDefense')
            final_timeline += basic_timeline_consolidation(timelines, 'endDefense')

            # Also consolidates climb seperately in order to seperate it
            # from intakes and placements.
            final_timeline.append(climb_consolidation(timelines))

            # Consolidates intakes and placements seperately, because
            # these are the main cycles of the game.
            final_timeline += cycle_consolidation(timelines)

            # Once the timeline is finally completed, it is sorted by
            # time, and added to the final timd.
            FINAL_TIMD['timeline'] = sorted(final_timeline, key=lambda action:
                                        float(action.get('time')))

