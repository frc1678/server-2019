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
# Internal imports
import consolidation
import decompress
import utils


# Check to ensure TIMD name is being passed as an argument
if len(sys.argv) == 2:
    # Extract TIMD name from system argument
    TIMD_NAME = sys.argv[1]
else:
    print('Error: TIMD name not being passed as an argument. Exiting...')
    sys.exit(0)

def avg(lis, exception=0.0):
    """Calculates the average of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    try:
        return sum(lis) / len(lis)
    except ZeroDivisionError:
        return exception

def percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action.get('didSucceed') for action in actions if
                 action.get('didSucceed') is not None]
    return round(100 * avg(successes))

def filter_cycles(cycle_list, **filters):
    """Puts cycles through filters to meet specific requirements

    cycle_list is a list of tuples where the first item is an intake and
    the second action is the placement or drop.
    filters are the specifications that certain data points inside the
    cycles must fit to be included in the returned cycles."""
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
                if cycle[1].get('level') == 2 or cycle[1].get('level') == 3:
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
    the intake, and the second item is the placement or drop.
    """
    cycle_times = []
    for cycle in cycles:
        cycle_times.append(float(cycle[0].get('time')) -
                           float(cycle[1].get('time')))
    return avg(cycle_times, None)

def calculate_total_cycle_time(cycles):
    """Calculates the total time for an action based on start and end times.

    Finds the time difference between each action pair passed and
    returns the sum of the differences.
    cycles is a list of tuples where both the first and second item in
    the tuple are actions, and the time between the actions is
    calculated.
    """
    cycle_times = []
    for cycle in cycles:
        cycle_times.append(float(cycle[0].get('time')) -
                           float(cycle[1].get('time')))
    return sum(cycle_times)

def filter_timeline_actions(timd, **filters):
    """Puts a timeline through a filter to use for calculations.

    timd is the TIMD that needs calculated data.
    filters are the specifications that certain data points inside the
    timeline must fit to be included in the returned timeline."""
    filtered_timeline = []
    # For each action, if any of the specifications are not met, the
    # loop breaks and it moves on to the next action, but if all the
    # specifications are met, it adds it to the filtered timeline.
    for action in timd.get('timeline'):
        for data_field, requirement in filters.items():
            # If the data_field requirement is level 1, it instead
            # checks for it not being level 2 or 3, because level 1 can
            # encompass all non-level 2 or 3 placement.
            if data_field == 'level' and requirement == 1:
                if action.get('level') == 2 or action.get('level') == 3:
                    break
            # If the filter specifies that the zone must be
            # leftLoadingStation, it means either loading station, so it
            # only breaks if the zone is not leftLoadingStation or
            # rightLoadingStation.
            elif data_field == 'zone' and requirement == 'leftLoadingStation':
                if action.get('zone') != 'leftLoadingStation' and \
                        action.get('zone') != 'rightLoadingStation':
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

def add_calculated_data_to_timd(timd):
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

    # The next set of calculated data points are the success
    # percentages, these are the percentages (displayed as an integer)
    # of didSucceed for certain actions, such as the percentage of
    # success a team has loading lemons.
    calculated_data['lemonLoadSuccess'] = percent_success(
        filter_timeline_actions(timd, type='intake', piece='lemon',
                                zone='leftLoadingStation'))
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
    cycle_list = [action for action in timd.get('timeline') if
                  action.get('type') == 'intake' or
                  action.get('type') == 'placement' or
                  action.get('type') == 'drop']
    if cycle_list != []:
        # If the first action in the list is a placement, it is a
        # preload, which doesn't count when calculating cycle times.
        if cycle_list[0].get('type') == 'placement':
            cycle_list.pop(0)
        # If the last action in the list is an intake, it means the
        # robot finished with a game object, in which the cycle was
        # never completed.
        if cycle_list[-1].get('type') == 'intake':
            cycle_list.pop(-1)
        paired_cycle_list = list(zip(*[iter(cycle_list)]*2))

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
            filter_cycles(paired_cycle_list, piece='lemon', level=1))
        calculated_data['lemonCycleL3'] = calculate_avg_cycle_time(
            filter_cycles(paired_cycle_list, piece='lemon', level=1))

    # Calculates if a team is incap throughout the entirety of the match
    # by checking if they have any actions in the match other than incap
    # and unincap. If they don't have any other actions, they were incap
    # the entire match.
    calculated_data['isIncapEntireMatch'] = False if [
        action for action in timd.get('timeline') if
        action.get('type') != 'incap' and
        action.get('type') != 'unIncap' and
        float(action.get('time')) <= 135.0] else True

    # Creates a list of the climb dictionary or nothing if there is no
    # climb. If there is a climb, the time of the climb is the amount
    # of time they spent climbing.
    climb_list = [action for action in timd.get('timeline') if
                  action.get('type') == 'climb']
    if climb_list:
        calculated_data['timeClimbing'] = climb_list[0].get('time')

    # Creates a list of all the incap and unincap actions in the timeline.
    incap_list = [action for action in timd.get('timeline') if
                  action.get('type') == 'incap' or
                  action.get('type') == 'unincap']
    if incap_list != []:
        # If the last action in the list is an incap, it means they
        # finished the match incap, so it adds an unicap at the end of
        # the timeline.
        if incap_list[-1].get('type') == 'incap':
            incap_list.append({'type': 'unIncap', 'time' : 0.0})
        paired_incap_list = list(zip(*[iter(incap_list)]*2))

        # Calculates the timeImpaired and timeIncap by calculating the
        # total amount of time the robot spent incap for either causes
        # that indicate the robot was impaired, or causes that indicate
        # the robot is incapacitated.
        calculated_data['timeImpaired'] = calculate_total_cycle_time(
            [cycle for cycle in paired_incap_list if
             cycle[0].get('cause') == 'brokenMechanism' or
             cycle[0].get('cause') == 'twoGamePieces'])
        calculated_data['timeIncap'] = calculate_total_cycle_time(
            [cycle for cycle in paired_incap_list if
             cycle[0].get('cause') != 'brokenMechanism' and
             cycle[0].get('cause') != 'twoGamePieces'])
    else:
        # Otherwise, the time that the robot spent impaired and incap is
        # naturally 0.
        calculated_data['timeImpaired'] = 0.0
        calculated_data['timeIncap'] = 0.0

    # Adds the calculated_data calculated throughout this function to
    # the final TIMD and returns it.
    timd['calculatedData'] = calculated_data
    return timd

COMPRESSED_TIMDS = []

TEMP_TIMDS = {}

# Goes into the temp_timds folder to get the names of all the tempTIMDs
# that correspond to the given TIMD.
for temp_timd in os.listdir(utils.create_file_path('data/cache/temp_timds')):
    if TIMD_NAME in temp_timd:
        file_path = utils.create_file_path(
            'data/cache/temp_timds/' + temp_timd)
        with open(file_path, 'r') as compressed_temp_timd:
            COMPRESSED_TIMDS.append(compressed_temp_timd.read())

# Iterates through all the compressed tempTIMDs and decompresses them.
# After decompressing them, adds them to the TEMP_TIMDS dictionary with
# the scout name as the key and their decompressed tempTIMD as a value.
# Does this in order to have a proper input to the consolidation
# function.
for compressed_temp_timd in COMPRESSED_TIMDS:
    decompressed_temp_timd = decompress.decompress_temp_timd(
        compressed_temp_timd)
    scout_name = decompressed_temp_timd.get('scoutName')
    # If there is no scout name in the temp_timd, it is faulty, so it
    # doesn't consolidate.
    if scout_name is not None:
        TEMP_TIMDS[scout_name] = decompressed_temp_timd

# After the TEMP_TIMDS are decompressed, they are fed into the
# consolidation script where they are returned as one final TIMD.
UNCALCULATED_TIMD = consolidation.consolidate_temp_timds(TEMP_TIMDS)

# Defines FINAL_TIMD as a version of the TIMD with calculated data
# using the add_calculated_data_to_timd function at the top of the file.
FINAL_TIMD = add_calculated_data_to_timd(UNCALCULATED_TIMD)

# Save data in local cache
with open(utils.create_file_path(f'data/cache/timds/{TIMD_NAME}.json'),
          'w') as file:
    json.dump(FINAL_TIMD, file)

# Save data in Firebase upload queue
with open(utils.create_file_path(
        f'data/upload_queue/timds/{TIMD_NAME}.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)
