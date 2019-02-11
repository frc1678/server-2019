#!/usr/bin/python3.7
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

COMPRESSED_TIMDS = []

TEMP_TIMDS = {}

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
    cycles is a list of tuples where the first action in the tuple is
    the starting time for an action, and the second is the end time for
    the action.
    """
    cycle_times = []
    for cycle in cycles:
        cycle_times.append(float(cycle[0].get('time')) -
                           float(cycle[1].get('time')))
    return sum(cycle_times)

def add_calculated_data_to_timd(timd):
    """Calculates data in a timd and adds it to 'calculatedData' in the TIMD.

    timd is the TIMD that needs calculated data."""
    calculated_data = {}

    # Adds counting data points to calculated data, does this by setting
    # the key to be the sum of a list of ones, one for each time the
    # given requirements are met. This creates the amount of times those
    # requirements were met in the timeline.
    calculated_data['orangesScored'] = len([
        action for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('didSucceed') is True and
        action.get('piece') == 'orange'])
    calculated_data['lemonsScored'] = len([
        action for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('didSucceed') is True and
        action.get('piece') == 'lemon'])
    calculated_data['orangeFouls'] = len([
        action for action in timd.get('timeline') if
        action.get('shotOutOfField') is True])
    calculated_data['lemonsSpilled'] = len([
        action for action in timd.get('timeline') if
        action.get('type') == 'spill'])

    # The next set of calculated data points are the success
    # percentages, these are the percentages (displayed as an integer)
    # of didSucceed for certain actions, such as the percentage of
    # success a team has loading lemons.
    calculated_data['lemonLoadSuccess'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'lemon' and
        (action.get('zone') == 'leftLoadingStation' or
         action.get('zone') == 'leftLoadingStation')]))

    calculated_data['orangeSuccessAll'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange']))
    calculated_data['orangeSuccessDefended'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is True]))
    calculated_data['orangeSuccessUndefended'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is False]))
    calculated_data['orangeSuccessL1'] = round(100.0 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['orangeSuccessL2'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 2]))
    calculated_data['orangeSuccessL3'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 3]))

    calculated_data['lemonSuccessAll'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon']))
    calculated_data['lemonSuccessDefended'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is True]))
    calculated_data['lemonSuccessUndefended'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is False]))
    calculated_data['lemonSuccessL1'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['lemonSuccessL2'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 2]))
    calculated_data['lemonSuccessL3'] = round(100 * avg([
        action['didSucceed'] for action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 3]))

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
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'orange'])
        calculated_data['orangeCycleL1'] = calculate_avg_cycle_time(
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'orange' and
             cycle[1].get('level') != 2 and
             cycle[1].get('level') != 3])
        calculated_data['orangeCycleL2'] = calculate_avg_cycle_time(
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'orange' and
             cycle[1].get('level') == 2])
        calculated_data['orangeCycleL3'] = calculate_avg_cycle_time(
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'orange' and
             cycle[1].get('level') == 3])

        calculated_data['lemonCycleAll'] = calculate_avg_cycle_time(
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'lemon'])
        calculated_data['lemonCycleL1'] = calculate_avg_cycle_time(
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'lemon' and
             cycle[1].get('level') != 2 and
             cycle[1].get('level') != 3])
        calculated_data['lemonCycleL2'] = calculate_avg_cycle_time(
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'lemon' and
             cycle[1].get('level') == 2])
        calculated_data['lemonCycleL3'] = calculate_avg_cycle_time(
            [cycle for cycle in paired_cycle_list if
             cycle[1].get('piece') == 'lemon' and
             cycle[1].get('level') == 3])

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
    TEMP_TIMDS[decompressed_temp_timd.get(
        'scoutName')] = decompressed_temp_timd

# After the TEMP_TIMDS are decompressed, they are fed into the
# consolidation script where they are returned as one final TIMD. This
# final TIMD is set as the variable name UNCALCULATED_TIMD.
UNCALCULATED_TIMD = consolidation.consolidate_temp_timds(TEMP_TIMDS)

# Defines FINAL_TIMD as a version of the TIMD with calculated data
# using the add_calculated_data_to_timd function at the top of the file.
FINAL_TIMD = add_calculated_data_to_timd(UNCALCULATED_TIMD)

# Save data in local cache
with open(utils.create_file_path('data/cache/timds/' + TIMD_NAME +
                                 '.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)

# Save data in Firebase upload queue
with open(utils.create_file_path('data/upload_queue/timds/' +
                                 TIMD_NAME + '.json'), 'w') as file:
    json.dump(FINAL_TIMD, file)
