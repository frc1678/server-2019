"""Functions that are used for the consolidation of tempTIMDs into one TIMD.

The main function in this file is consolidate_temp_timds(), which is
called in calculate_timd.py."""
# External imports
import collections
import numpy as np
# No internal imports

def consolidate_times(times, sprking):
    """Takes in multiple time options and consolidates them into one time.

    times is a dictionary of each scout to their respective time value."""

    # If any time is in the wrong time period (has an *) it is not
    # considered for time consolidation.
    # Checks if all of the times end in an asterisk
    if all([time[-1] == '*' for time in times.values()]):
        # If all the times end in asterisks, they are in the wrong time
        # period. To fix the time period, all wrong times in sandstorm
        # (time >= 135.1) are set to teleop as 135.0, and all wrong
        # times in teleop (time <= 135.0) are set to sandstorm as 135.1.
        altered_asterisk_times = {}
        for scout, time in times.items():
            if float(time.split('*')[0]) >= 135.1:
                altered_asterisk_times[scout] = 135.0
            else:
                altered_asterisk_times[scout] = 135.1
        return max_occurrences(altered_asterisk_times, sprking)
    else:
        for scout, time in times.items():
            if '*' in time:
                times.pop(scout)

    # Creates a list of the times in the form of floats instead of their
    # tempTIMD format of strings. Does this in order to  use them for
    # calculations.
    float_list = [float(time) for time in times.values()]

    # Finds the mean and standard deviation for the array of floats,
    # these metrics are used for the reciprocal z-scores used later on.
    mean = np.mean(float_list)
    std = np.std(float_list)

    # If the standard deviation is zero, all the times are the same, so
    # it just returns the mean.
    if std == 0:
        return format(mean, '.1f')

    # Creates a list of tuples with the first item as the time and the
    # second item as the weight (squared reciprocal of the z-score for
    # each time). These values are how much each time is weighted when
    # calculating the final weighted average. The lower the value on
    # this list the time is, the farther away from the mean it is, and
    # the less it is weighted.
    reciprocal_zscores = [(number, (1 / ((mean - number) / std)) ** 2)
                          for number in float_list]

    # Multiplies each time by its corresponding reciprocal z-score
    # value, creating a weighted time.
    weighted_times = [number * zscore_weight for number, zscore_weight
                      in reciprocal_zscores]

    # Adds up all the weighted times and divides it by the sum of the
    # reciprocal_zscore_list. Does this in order to get a reasonable
    # time, if this step is not taken, the weighted time makes no sense.
    weighted_average = sum(weighted_times) / sum([zscore[1] for zscore \
        in reciprocal_zscores])

    # Formats each average to a float with one decimal place.
    return format(weighted_average, '.1f')

def max_occurrences(comparison_list, sprking):
    """Takes in a dictionary of scouts to their value and returns the majority.

    If there is no clear winner, returns the value for the best spr
    scout.

    comparison_list is a dictionary of each of the scouts to their input
    on a specific decision (value for a data field, amount of actions,
    etc).
    sprking is the scout with the best spr out of the scouts, used if
    there is no clear majority."""

    # Each item in the list to how many times it appeared in the list.
    # Uses the collections module to count how many appearances each
    # item has in the list.
    occurence_list = dict(collections.Counter(comparison_list.values()))

    # If the highest occurence on the occurence list is the same as
    # the lowest occurence, the correct value for the datapoint is
    # the value output by the scout with the best spr. This triggers
    # both when all the scout values are the same (The max and min
    # would both be three) and when all the scout values are
    # different (The max and min are both 1). In the case of any
    # other scenario, the max is trusted because it would suggest
    # the max is the 2 in a 2 scout versus 1 split decision.
    if max(occurence_list.values()) == min(occurence_list.values()):
        return comparison_list[sprking]
    else:
        return max(occurence_list, key=occurence_list.get)

def consolidate_timeline_action(temp_timd_timelines, action_type, sprking):
    """Takes an action type out of timelines and consolidates it seperately.

    Returns a consolidated timeline only made up of the action type that
    was passed as action_type.

    input_timelines is the dictionary of the scouts to their specific
    timelines.
    action_type is the action type that the function is consolidating.
    sprking is the scout with the best spr out of the scouts, used when
    max_occurrences is called."""

    # The dictionary of three timelines with only the types specified
    # in the function.
    simplified_timelines = {scout : [] for scout in temp_timd_timelines.keys()}

    # Takes the three different timelines and cuts out any types of
    # data points which are not the specified types.
    for scout, timeline in temp_timd_timelines.items():
        for action in timeline:
            if action.get('type') == action_type:
                simplified_timelines[scout].append(action)

    # Scouts to the amount of actions of the specified type are in the
    # timeline.
    count_timelines = {scout : len(timeline) for
                       scout, timeline in simplified_timelines.items()}

    # Finds the majority amount of actions in the timeline to see
    # which amount of actions is the correct amount.
    majority_length = max_occurrences(count_timelines, sprking)

    # Creates a dictionary of scouts to their timelines which follow the
    # majority length of timeline.
    correct_length_timelines = {}
    for scout, timeline_length in count_timelines.items():
        if timeline_length == majority_length:
            correct_length_timelines[scout] = simplified_timelines[scout]

    # If there are scouts that don't agree with the majority timeline,
    # creates a time_reference to line up against.
    time_reference = {}
    if sprking in correct_length_timelines.keys():
        correct_scout = sprking
    else:
        correct_scout = list(correct_length_timelines.keys())[-1]
    reference_timeline = correct_length_timelines[correct_scout]
    time_reference[correct_scout] = [action['time'] for action in
                                     reference_timeline]

    # If there are scouts that do not agree with the correct timeline
    # length, find out which of their action times agree with the time
    # reference the best, and line it up against the reference in the
    # correct_length_timelines dictionary.
    for scout in simplified_timelines.keys():
        if scout not in correct_length_timelines.keys():
            correct_length_timelines[scout] = [{} for action in
                                               range(majority_length)]
            # In order to find the best option for timings, it sets
            # up a matrix of time differences between each action in
            # each tempTIMD.
            timings = np.zeros((len(simplified_timelines[scout]),
                                majority_length))
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
            while timings.size > 0:
                # lowest_index is in the format of ([y coordinate],
                # [x coordinate]), which requires lowest_index[1][0] to
                # get the x coordinate, and lowest_index[0][0] for the y
                # coordinate.
                lowest_index = np.where(timings == timings.min())
                correct_length_timelines[scout][lowest_index[1][0]] = \
                    simplified_timelines[scout][lowest_index[0][0]]
                timings = np.delete(timings, int(lowest_index[1][0]), axis=1)
                timings = np.delete(timings, int(lowest_index[0][0]), axis=0)

    final_simplified_timd = [{} for action in range(majority_length)]
    # Iterates through the sprking's timeline to compare all the actions.
    for action_index, action in enumerate(correct_length_timelines[sprking]):
        comparison_dict = {scout : timeline[action_index] for scout,
                           timeline in correct_length_timelines.items()}
        for key in comparison_dict[sprking].keys():
            # For every key that isn't time, which can't realistically
            # have a majority, the majority opinion is set to the final
            # timd.
            scout_to_keys = {scout : action.get(key) for scout,
                             action in comparison_dict.items()}

            if key == 'time':
                # If the key is time, finds the correct time using the
                # consolidate_times algorithm.
                final_simplified_timd[action_index]['time'] = \
                    consolidate_times(scout_to_keys, sprking)
            else:
                # For every key in the dictionary other than time, it just
                # takes the majority value for the key.
                final_simplified_timd[action_index][key] = \
                    max_occurrences(scout_to_keys, sprking)

    # Returns the final created timeline
    return final_simplified_timd

def climb_consolidation(input_timelines, sprking):
    """Takes climb out of the timelines of the tempTIMDs and consolidates it.

    Returns a timeline only with climb inside it to add to the final
    timeline for the timd.

    input_timelines is the dictionary of the scouts to their specific
    timelines.
    sprking is the scout with the best spr out of the scouts, used when
    max_occurrences is called. More info in the docstring for
    max_occurrences.
    """

    # Scout name to climb dictionary.
    simplified_timelines = {}

    # Fills in 'simplified_timelines' with the scout and the climb
    # dictionary from the three tempTIMDs.
    for scout, timeline in input_timelines.items():
        for action in timeline:
            if action.get('type') == 'climb':
                simplified_timelines[scout] = action

    final_simplified_timd = {'type': 'climb', 'attempted': {}, 'actual': {}}

    # Consolidates time first
    final_simplified_timd['time'] = consolidate_times({
        scout: climb['time'] for scout,
        climb in simplified_timelines.items()}, sprking)

    for key in ['attempted', 'actual']:
        for robot in ['self', 'robot1', 'robot2']:
            final_simplified_timd[key][robot] = max_occurrences({
                scout: climb[key][robot] for scout, climb in
                simplified_timelines.items()}, sprking)

    # Returns the final created timeline
    return final_simplified_timd

def consolidate_temp_timds(temp_timds):
    """Consolidates between 1-3 temp_timds into one final timd.

    This is the main function of consolidation.py, and is called by
    calculate_timd.py.
    temp_timds is a dictionary with scout names as keys and their
    respective tempTIMD as a value.
    """

    # 'sprking' is the scout with the best (lowest) SPR
    #TODO: Implement spr system
    sprking = list(temp_timds.keys())[0]

    final_timd = {}
    # Iterates through the keys of the best scout's tempTIMD and
    # consolidates each data_field one at a time.
    for data_field in list(temp_timds[sprking]):
        if data_field == 'timeline':
            # In order to compute the timeline properly, it is split
            # into a list of the timelines.
            timelines = {}
            for scout, temp_timd in temp_timds.items():
                temp_timeline = temp_timd.get('timeline', [])
                timelines[scout] = temp_timeline

            # If the list of timelines only includes one timeline, that
            # timeline is taken as the correct one and put into the
            # final TIMD.
            if len(timelines.values()) == 1:
                # Converts all times to floats and removes asterisk to
                # put it into the format of a timd.
                final_timeline = []
                for action in timelines[sprking]:
                    action_time = action.get('time')
                    # Takes the time before the asterisk, if there is no
                    # asterisk, .split() still returns a list, a list of
                    # only the time, meaning [0] works in both
                    # instances.
                    action['time'] = float(action_time.split('*')[0])
                final_timd['timeline'] = timelines[sprking]

            # If the list has more than one tempTIMD, the process for
            # computation has to be split up by each of the types of
            # actions in the timeline.
            else:
                # Creates the final timeline which is passed as the
                # timeline for the final timd at the end of
                # consolidation.
                final_timeline = []

                # Seperates all the basic actions out and consolidates
                # them one at a time. All the actions are consolidated
                # seperately so that the timings on each action are
                # split apart, making it more easy to line up, identify,
                # and consolidate the timeline.
                for action_type in ['spill', 'incap', 'unincap', \
                        'drop', 'startDefense', 'endDefense', \
                        'placement', 'intake']:
                    final_timeline += consolidate_timeline_action(
                        timelines, action_type, sprking)

                # Also consolidates climb seperately in order to
                # seperate it from intakes and placements. Climb needs a
                # seperate function because of its relatively strange
                # structure.
                final_timeline.append(climb_consolidation(timelines, sprking))

                # Once the timeline is finally completed, it is sorted
                # by time, and added to the final timd.
                final_timd['timeline'] = sorted(final_timeline, \
                    key=lambda action: float(action.get('time')))

        # When consolidating non-timed keys, it is easy to consolidate
        # them, as you can simply find which value is the most common in
        # the set of three possibilities. The other data_fields that
        # are not included in this set, such as timerStarted, are scout
        # diagnostics, and not included in the final TIMD.
        elif data_field not in ['timeline', 'timerStarted',
                                'currentCycle', 'scoutID', 'scoutName',
                                'appVersion', 'assignmentMode',
                                'assignmentFileTimestamp',
                                'matchesNotScouted']:

            # Creates a dictionary of each scout to the key from their
            # tempTIMD to compare against each other. (Code note - This
            # code is using .get and not simply referencing the key out
            # of the dictionary because .get doesn't error out when the
            # key doesn't exist. It instead returns NoneType).
            data_field_comparison_list = {}
            for scout, temp_timd in temp_timds.items():
                temp_data_field = temp_timd.get(data_field)
                if temp_data_field is not None:
                    data_field_comparison_list[scout] = temp_data_field

            # Uses the max_occurrences function to find the correct value
            # for the data field.
            data_occurence_max = max_occurrences(
                data_field_comparison_list, sprking)

            final_timd[data_field] = data_occurence_max

    return final_timd
