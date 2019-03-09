#!/usr/bin/python3.6
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
# External imports
import json
import os
import sys
import subprocess
# Internal imports
import consolidation
import decompressor
import utils

def avg(lis, exception=0.0):
    """Calculates the average of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        return sum(lis) / len(lis)

def percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action.get('didSucceed') for action in actions]
    # Returns the integer percentage of times in successes that
    # didSucceed is true. Taking an average of a list of booleans
    # returns a float between 0 and 1 of what percentage of times the
    # value was True.
    # Example: [True, True, False, True] returns 75.
    return round(100 * avg(successes))

def filter_cycles(cycle_list, **filters):
    """Puts cycles through filters to meet specific requirements

    cycle_list is a list of tuples where the first item is an intake and
    the second action is the placement or drop.
    filters are the specifications that certain data points inside the
    cycles must fit to be included in the returned cycles.
    example for filter - 'level=1' as an argument, '{'level': 1}' inside
    the function."""
    filtered_cycles = []
    # For each cycle, if any of the specifications are not met, the
    # loop breaks and it moves on to the next cycle, but if all the
    # specifications are met, it adds it to the filtered cycles.
    for cycle in cycle_list:
        for data_field, requirement in filters.items():
            # If the data_field requirement is level 1, it instead
            # checks for it not being level 2 or 3, because level 1 can
            # encompass all non-level 2 or 3 placement.
            if data_field == 'level' and requirement == 1:
                if cycle[1].get('level', 1) != 1:
                    break
            # Otherwise, it checks the requirement normally
            else:
                if cycle[1].get(data_field) != requirement:
                    break
        # If all the requirements are met, it adds the cycle to the
        # returned filtered cycles.
        else:
            filtered_cycles.append(cycle)
    return filtered_cycles

def calculate_avg_cycle_time(cycles):
    """Calculates the average time for an action based on start and end times.

    Finds the time difference between each action pair passed and
    returns the average of the differences.
    cycles is a list of tuples where the first action in the tuple is
    the intake, and the second item is the placement or drop."""
    cycle_times = []
    for cycle in cycles:
        # Subtracts the second time from the first because the time
        # counts down in the timeline.
        cycle_times.append(cycle[0].get('time') -
                           cycle[1].get('time'))
    return avg(cycle_times, None)

def calculate_total_action_duration(cycles):
    """Calculates the total duration for an action based on start and end times.

    Finds the time difference between each action pair passed and
    returns the sum of the differences.  Used for both defense and incap
    cycles.

    cycles is a list of tuples where the first action marks the start of
    a period (incap or defense), and the second action marks the end of
    that period."""
    cycle_times = []
    for cycle in cycles:
        # Subtracts the second time from the first because the time
        # counts down in the timeline.
        cycle_times.append(cycle[0].get('time') -
                           cycle[1].get('time'))
    return sum(cycle_times)

def filter_timeline_actions(timd, **filters):
    """Puts a timeline through a filter to use for calculations.

    timd is the TIMD that needs calculated data.
    filters are the specifications that certain data points inside the
    timeline must fit to be included in the returned timeline.
    example for filter - 'level=1' as an argument, '{'level': 1}' inside
    the function."""
    filtered_timeline = []
    # For each action, if any of the specifications are not met, the
    # loop breaks and it moves on to the next action, but if all the
    # specifications are met, it adds it to the filtered timeline.
    for action in timd.get('timeline', []):
        for data_field, requirement in filters.items():
            # If the data_field requirement is level 1, it instead
            # checks for it not being level 2 or 3, because level 1 can
            # encompass all non-level 2 or 3 placement.
            if data_field == 'level' and requirement == 1:
                if action.get('level', 1) != 1:
                    break
            # If the filter specifies that the zone must be
            # loadingStation, it means either loading station, so it
            # only breaks if the zone is not leftLoadingStation or
            # rightLoadingStation.
            elif data_field == 'zone' and requirement == 'loadingStation':
                if action['zone'] not in ['leftLoadingStation',
                                          'rightLoadingStation']:
                    break
            # If the filter specifies time, it can either specify
            # sandstorm by making the requirement 'sand' or specify
            # teleop by making the requirement 'tele'.
            #TODO: Rename 'sand' and 'tele'
            elif data_field == 'time':
                if requirement == 'sand' and action['time'] <= 135.0:
                    break
                elif requirement == 'tele' and action['time'] > 135.0:
                    break
            # Otherwise, it checks the requirement normally
            else:
                if action.get(data_field) != requirement:
                    break
        # If all the requirements are met, it adds the action to the
        # returned filtered timeline.
        else:
            filtered_timeline.append(action)
    return filtered_timeline

def make_paired_cycle_list(cycle_list):
    """Pairs up cycles together into tuples.

    cycle_list is the list of actions that need to be paired up."""
    # [::2] are the even-indexed items of the list, [1::2] are the
    # odd-indexed items of the list. The python zip function puts
    # matching-index items from two lists into tuples.
    return list(zip(cycle_list[::2], cycle_list[1::2]))

def calculate_timd_data(timd):
    """Calculates data in a timd and adds it to 'calculatedData' in the TIMD.

    timd is the TIMD that needs calculated data."""
    calculated_data = {}

    # Adds counting data points to calculated data, does this by setting
    # the key to be the sum of a list of ones, one for each time the
    # given requirements are met. This creates the amount of times those
    # requirements were met in the timeline.
    calculated_data['orangesScored'] = len(filter_timeline_actions(
        timd, type='placement', didSucceed=True, piece='orange'))
    calculated_data['lemonsScored'] = len(filter_timeline_actions(
        timd, type='placement', didSucceed=True, piece='lemon'))
    calculated_data['orangeFouls'] = len(filter_timeline_actions(
        timd, shotOutOfField=True))
    calculated_data['lemonsSpilled'] = len(filter_timeline_actions(
        timd, type='spill'))

    calculated_data['orangesScoredSandstorm'] = len(
        filter_timeline_actions(timd, type='placement', piece='orange', \
        didSucceed=True, time='sand'))
    calculated_data['lemonsScoredSandstorm'] = len(
        filter_timeline_actions(timd, type='placement', piece='lemon', \
        didSucceed=True, time='sand'))
    calculated_data['orangesScoredTeleL1'] = len(
        filter_timeline_actions(timd, type='placement', piece='orange', \
        level=1, didSucceed=True, time='tele'))
    calculated_data['orangesScoredTeleL2'] = len(
        filter_timeline_actions(timd, type='placement', piece='orange', \
        level=2, didSucceed=True, time='tele'))
    calculated_data['orangesScoredTeleL3'] = len(
        filter_timeline_actions(timd, type='placement', piece='orange', \
        level=3, didSucceed=True, time='tele'))
    calculated_data['lemonsScoredTeleL1'] = len(
        filter_timeline_actions(timd, type='placement', piece='lemon', \
        level=1, didSucceed=True, time='tele'))
    calculated_data['lemonsScoredTeleL2'] = len(
        filter_timeline_actions(timd, type='placement', piece='lemon', \
        level=2, didSucceed=True, time='tele'))
    calculated_data['lemonsScoredTeleL3'] = len(
        filter_timeline_actions(timd, type='placement', piece='lemon', \
        level=3, didSucceed=True, time='tele'))

    calculated_data['orangesScoredL1'] = len(
        filter_timeline_actions(timd, type='placement', piece='orange', \
        level=1, didSucceed=True))
    calculated_data['orangesScoredL2'] = len(
        filter_timeline_actions(timd, type='placement', piece='orange', \
        level=2, didSucceed=True))
    calculated_data['orangesScoredL3'] = len(
        filter_timeline_actions(timd, type='placement', piece='orange', \
        level=3, didSucceed=True))
    calculated_data['lemonsScoredL1'] = len(
        filter_timeline_actions(timd, type='placement', piece='lemon', \
        level=1, didSucceed=True))
    calculated_data['lemonsScoredL2'] = len(
        filter_timeline_actions(timd, type='placement', piece='lemon', \
        level=2, didSucceed=True))
    calculated_data['lemonsScoredL3'] = len(
        filter_timeline_actions(timd, type='placement', piece='lemon', \
        level=3, didSucceed=True))

    calculated_data['totalCyclesDefended'] = sum([
        action['cyclesDefended'] for action in
        filter_timeline_actions(timd, type='endDefense')])

    # The next set of calculated data points are the success
    # percentages, these are the percentages (displayed as an integer)
    # of didSucceed for certain actions, such as the percentage of
    # success a team has loading lemons.
    calculated_data['lemonLoadSuccess'] = percent_success(
        filter_timeline_actions(timd, type='intake', piece='lemon',
                                zone='loadingStation'))
    calculated_data['orangeSuccessAll'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='orange'))
    calculated_data['orangeSuccessDefended'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='orange',
                                wasDefended=True))
    calculated_data['orangeSuccessUndefended'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='orange',
                                wasDefended=False))
    calculated_data['orangeSuccessL1'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='orange',
                                level=1))
    calculated_data['orangeSuccessL2'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='orange',
                                level=2))
    calculated_data['orangeSuccessL3'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='orange',
                                level=3))

    calculated_data['lemonSuccessAll'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='lemon'))
    calculated_data['lemonSuccessDefended'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='lemon',
                                wasDefended=True))
    calculated_data['lemonSuccessUndefended'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='lemon',
                                wasDefended=False))
    calculated_data['lemonSuccessL1'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='lemon',
                                level=1))
    calculated_data['lemonSuccessL2'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='lemon',
                                level=2))
    calculated_data['lemonSuccessL3'] = percent_success(
        filter_timeline_actions(timd, type='placement', piece='lemon',
                                level=3))

    # Creates the cycle_list, a list of tuples where the intake is the
    # first item and the placement or drop is the second. This is used
    # when calculating cycle times.
    cycle_list = []
    for action in timd.get('timeline', []):
        if action.get('type') in ['intake', 'placement', 'drop']:
            # If the action is a failed loading station intake, it
            # shouldn't play a part in cycles, so it is filtered out.
            if not (action.get('type') == 'intake' and
                    action.get('didSucceed') is False):
                cycle_list.append(action)

    # There must be at least 2 actions to have a cycle
    if len(cycle_list) > 1:
        # If the first action in the list is a placement, it is a
        # preload, which doesn't count when calculating cycle times.
        if cycle_list[0].get('type') in ['placement', 'drop']:
            cycle_list.pop(0)
        # If the last action in the list is an intake, it means the
        # robot finished with a game object, in which the cycle was
        # never completed.
        if cycle_list[-1].get('type') == 'intake':
            cycle_list.pop(-1)
        paired_cycle_list = make_paired_cycle_list(cycle_list)

        calculated_data['orangeCycleAll'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='orange'))
        calculated_data['orangeCycleL1'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='orange', level=1))
        calculated_data['orangeCycleL2'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='orange', level=2))
        calculated_data['orangeCycleL3'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='orange', level=3))

        calculated_data['lemonCycleAll'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='lemon'))
        calculated_data['lemonCycleL1'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='lemon', level=1))
        calculated_data['lemonCycleL2'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='lemon', level=2))
        calculated_data['lemonCycleL3'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='lemon', level=3))

    # Calculates if a team is incap throughout the entirety of the match
    # by checking if they have any actions in the match other than incap
    # and unincap. If they don't have any other actions, they were incap
    # the entire match.
    for action in timd.get('timeline', []):
        if action.get('type') not in ['incap', 'unincap'] and \
                action.get('time') <= 135.0:
            calculated_data['isIncapEntireMatch'] = False
            break
    else:
        calculated_data['isIncapEntireMatch'] = True

    # Creates a list of the climb dictionary or nothing if there is no
    # climb. If there is a climb, the time of the climb is the amount
    # of time they spent climbing.
    for action in timd.get('timeline', []):
        if action['type'] == 'climb':
            calculated_data['timeClimbing'] = action['time']

    # Creates a list of all the incap and unincap actions in the timeline.
    incap_items = []
    for action in timd.get('timeline', []):
        if action.get('type') in ['incap', 'unincap']:
            incap_items.append(action)
    if len(incap_items) > 0:
        # If the last action in the list is an incap, it means they
        # finished the match incap, so it adds an unincap at the end of
        # the timeline.
        if incap_items[-1]['type'] == 'incap':
            incap_items.append({'type': 'unincap', 'time': 0.0})
        paired_incap_list = make_paired_cycle_list(incap_items)

        # Calculates the timeIncap by calculating the total amount of
        # time the robot spent incap during the match.
        calculated_data['timeIncap'] = calculate_total_action_duration(
            paired_incap_list)
    else:
        # Otherwise, the time that the robot spent incap is naturally 0.
        calculated_data['timeIncap'] = 0.0

    # Creates a list of all the startDefense and endDefense actions in
    # the timeline.
    defense_items = []
    for action in timd.get('timeline', []):
        if action['type'] in ['startDefense', 'endDefense']:
            defense_items.append(action)
    if len(defense_items) > 0:
        paired_defense_list = make_paired_cycle_list(defense_items)

        # 'timeDefending' is the total amount of time the robot spent
        # defending during the match.
        calculated_data['timeDefending'] = calculate_total_action_duration(
            paired_defense_list)
    else:
        # Otherwise, the time that the robot spent defending is naturally 0.
        calculated_data['timeDefending'] = 0.0
    return calculated_data

# Check to ensure TIMD name is being passed as an argument
if len(sys.argv) == 2:
    # Extract TIMD name from system argument
    TIMD_NAME = sys.argv[1]
else:
    print('Error: TIMD name not being passed as an argument. Exiting...')
    sys.exit(0)

COMPRESSED_TIMDS = []

TEMP_TIMDS = {}

# Goes into the temp_timds folder to get the names of all the tempTIMDs
# that correspond to the given TIMD. Afterwards, it decompresses them
# and adds them to the TEMP_TIMDS dictionary with the scout name as the
# key and their decompressed tempTIMD as a value. Does this in order to
# have a proper input to the consolidation function.
for temp_timd in os.listdir(utils.create_file_path('data/cache/temp_timds')):
    if temp_timd.split('-')[0] == TIMD_NAME:
        file_path = utils.create_file_path(
            f'data/cache/temp_timds/{temp_timd}')
        with open(file_path, 'r') as file:
            compressed_temp_timd = file.read()
        decompressed_temp_timd = list(decompressor.decompress_temp_timd(
            compressed_temp_timd).values())[0]
        scout_name = decompressed_temp_timd.get('scoutName')
        TEMP_TIMDS[scout_name] = decompressed_temp_timd

# After the TEMP_TIMDS are decompressed, they are fed into the
# consolidation script where they are returned as one final TIMD.
FINAL_TIMD = consolidation.consolidate_temp_timds(TEMP_TIMDS)

# Adds the matchNumber and teamNumber necessary for later team calcs.
FINAL_TIMD['matchNumber'] = int(TIMD_NAME.split('Q')[1])
FINAL_TIMD['teamNumber'] = int(TIMD_NAME.split('Q')[0])

# Adds calculatedData to the FINAL_TIMD using the
# add_calculated_data_to_timd function at the top of the file.
FINAL_TIMD['calculatedData'] = calculate_timd_data(FINAL_TIMD)

# Save data in local cache
with open(utils.create_file_path(f'data/cache/timds/{TIMD_NAME}.json'),
          'w') as file:
    json.dump(FINAL_TIMD, file)

# Save data in Firebase upload queue
with open(utils.create_file_path(
        f'data/upload_queue/timds/{TIMD_NAME}.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)

# TODO: Make 'forward_temp_super' more efficient (call it less often)
subprocess.call(f'python3 forward_temp_super.py', shell=True)

# After the timd is calculated, the team is calculated.
TEAM = TIMD_NAME.split('Q')[0]
subprocess.call(f'python3 calculate_team.py {TEAM}', shell=True)
