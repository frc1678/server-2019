#!/usr/bin/python3.6
"""Calculations for a single Team.

Team calculations include the calculation of data points that are
reflective of a team's performance across all of their matches.

Called by server.py with the number of the Team to be calculated."""
# External imports
import json
import os
import sys
import math
import numpy as np
# Internal imports
import utils

# Name of team calculated average data field to the respective timd data
# field.
AVERAGE_DATA_FIELDS = {
    'avgOrangesScored': 'orangesScored',
    'avgLemonsScored': 'lemonsScored',
    'avgOrangesFouls': 'orangeFouls',
    'avgPinningFouls': 'pinningFouls',
    'avgOrangesScoredSandstorm': 'orangesScoredSandstorm',
    'avgLemonsScoredSandstorm': 'lemonsScoredSandstorm',
    'avgOrangesScoredTeleL1': 'orangesScoredTeleL1',
    'avgOrangesScoredTeleL2': 'orangesScoredTeleL2',
    'avgOrangesScoredTeleL3': 'orangesScoredTeleL3',
    'avgLemonsScoredTeleL1': 'lemonsScoredTeleL1',
    'avgLemonsScoredTeleL2': 'lemonsScoredTeleL2',
    'avgLemonsScoredTeleL3': 'lemonsScoredTeleL3',
    'avgOrangesScoredL1': 'orangesScoredL1',
    'avgOrangesScoredL2': 'orangesScoredL2',
    'avgOrangesScoredL3': 'orangesScoredL3',
    'avgLemonsScoredL1': 'lemonsScoredL1',
    'avgLemonsScoredL2': 'lemonsScoredL2',
    'avgLemonsScoredL3': 'lemonsScoredL3',
    'avgOrangeCycles': 'orangeCycles',
    'avgLemonCycles': 'lemonCycles',
    'avgOrangeDrops': 'orangeDrops',
    'avgLemonDrops': 'lemonDrops',
    'avgOrangeFails': 'orangeFails',
    'avgLemonFails': 'lemonFails',
    'avgTimeIncap': 'timeIncap',
    'avgTimeClimbing': 'timeClimbing',
    'avgOrangePointsPrevented': 'orangePointsPrevented',
    'avgLemonPointsPrevented': 'lemonPointsPrevented',
    'avgPointsPrevented': 'pointsPrevented',
}

# Name of team calculated average data field of the last four matches to
# the respective timd data field.
LFM_AVERAGE_DATA_FIELDS = {
    'lfmAvgOrangesScored': 'orangesScored',
    'lfmAvgLemonsScored': 'lemonsScored',
    'lfmAvgOrangesFouls': 'orangeFouls',
    'lfmAvgPinningFouls': 'pinningFouls',
    'lfmAvgTimeIncap': 'timeIncap',
    'lfmAvgTimeClimbing': 'timeClimbing',
}

# Name of team calculated standard deviation data field to the
# respective timd data field.
SD_DATA_FIELDS = {
    'sdAvgOrangesScored': 'orangesScored',
    'sdAvgLemonsScored': 'lemonsScored',
    'sdAvgOrangesFouls': 'orangeFouls',
    'sdAvgPinningFouls': 'pinningFouls',
    'sdAvgTimeIncap': 'timeIncap',
    'sdAvgTimeClimbing': 'timeClimbing',
}

# Name of team calculated upper half average data field to the
# respective timd data field.
P75_DATA_FIELDS = {
    'p75AvgOrangesScored': 'orangesScored',
    'p75AvgLemonsScored': 'lemonsScored',
    'p75AvgOrangesFouls': 'orangeFouls',
    'p75AvgPinningFouls': 'pinningFouls',
    'p75AvgTimeIncap': 'timeIncap',
    'p75AvgTimeClimbing': 'timeClimbing',
}

# Name of the team calculated success data field to the respective timd
# data field.
SUCCESS_DATA_FIELDS = {
    'lemonLoadSuccess': {
        'type': 'intake',
        'piece': 'lemon',
        'zone': 'loadingStation',
    },
    'orangeSuccessAll': {
        'type': 'placement',
        'piece': 'orange',
    },
    'orangeSuccessDefended': {
        'type': 'placement',
        'piece': 'orange',
        'wasDefended': True,
    },
    'orangeSuccessUndefended': {
        'type': 'placement',
        'piece': 'orange',
        'wasDefended': False,
    },
    'orangeSuccessL1': {
        'type': 'placement',
        'piece': 'orange',
        'level': 1,
    },
    'orangeSuccessL2': {
        'type': 'placement',
        'piece': 'orange',
        'level': 2,
    },
    'orangeSuccessL3': {
        'type': 'placement',
        'piece': 'orange',
        'level': 3,
    },
    'lemonSuccessAll': {
        'type': 'placement',
        'piece': 'lemon',
    },
    'lemonSuccessDefended': {
        'type': 'placement',
        'piece': 'lemon',
        'wasDefended': True,
    },
    'lemonSuccessUndefended': {
        'type': 'placement',
        'piece': 'lemon',
        'wasDefended': False,
    },
    'lemonSuccessL1': {
        'type': 'placement',
        'piece': 'lemon',
        'level': 1,
    },
    'lemonSuccessL2': {
        'type': 'placement',
        'piece': 'lemon',
        'level': 2,
    },
    'lemonSuccessL3': {
        'type': 'placement',
        'piece': 'lemon',
        'level': 3,
    },
    'lemonSuccessFromSide': {
        'type': 'placement',
        'piece': 'lemon',
        'side': ('near', True),
    },
}

# Name of the team calculated success data field of the last four
# matches to the respective timd data field.
LFM_SUCCESS_DATA_FIELDS = {
    'lfmLemonLoadSuccess': {
        'type': 'intake',
        'piece': 'lemon',
        'zone': 'loadingStation',
    },
    'lfmOrangeSuccessAll': {
        'type': 'placement',
        'piece': 'orange',
    },
    'lfmOrangeSuccessDefended': {
        'type': 'placement',
        'piece': 'orange',
        'wasDefended': True,
    },
    'lfmOrangeSuccessUndefended': {
        'type': 'placement',
        'piece': 'orange',
        'wasDefended': False,
    },
    'lfmOrangeSuccessL1': {
        'type': 'placement',
        'piece': 'orange',
        'level': 1,
    },
    'lfmOrangeSuccessL2': {
        'type': 'placement',
        'piece': 'orange',
        'level': 2,
    },
    'lfmOrangeSuccessL3': {
        'type': 'placement',
        'piece': 'orange',
        'level': 3,
    },
    'lfmLemonSuccessAll': {
        'type': 'placement',
        'piece': 'lemon',
    },
    'lfmLemonSuccessDefended': {
        'type': 'placement',
        'piece': 'lemon',
        'wasDefended': True,
    },
    'lfmLemonSuccessUndefended': {
        'type': 'placement',
        'piece': 'lemon',
        'wasDefended': False,
    },
    'lfmLemonSuccessL1': {
        'type': 'placement',
        'piece': 'lemon',
        'level': 1,
    },
    'lfmLemonSuccessL2': {
        'type': 'placement',
        'piece': 'lemon',
        'level': 2,
    },
    'lfmLemonSuccessL3': {
        'type': 'placement',
        'piece': 'lemon',
        'level': 3,
    },
    'lfmLemonSuccessFromSide': {
        'type': 'placement',
        'piece': 'lemon',
        'side': ('near', True),
    },
}

# Name of the team calculated average cycle time data field to the
# timeline filters specified.
CYCLE_DATA_FIELDS = {
    'orangeCycleAll': {
        'piece': 'orange',
    },
    'orangeCycleL1': {
        'piece': 'orange',
        'level': 1,
    },
    'orangeCycleL2': {
        'piece': 'orange',
        'level': 2,
    },
    'orangeCycleL3': {
        'piece': 'orange',
        'level': 3,
    },
    'lemonCycleAll': {
        'piece': 'lemon',
    },
    'lemonCycleL1': {
        'piece': 'lemon',
        'level': 1,
    },
    'lemonCycleL2': {
        'piece': 'lemon',
        'level': 2,
    },
    'lemonCycleL3': {
        'piece': 'lemon',
        'level': 3,
    },
}

# Name of the team calculated standard deviation cycle time data field
# to the timeline filters specified.
SD_CYCLE_DATA_FIELDS = {
    'sdOrangeCycleAll': {
        'piece': 'orange',
    },
    'sdOrangeCycleL1': {
        'piece': 'orange',
        'level': 1,
    },
    'sdOrangeCycleL2': {
        'piece': 'orange',
        'level': 2,
    },
    'sdOrangeCycleL3': {
        'piece': 'orange',
        'level': 3,
    },
    'sdLemonCycleAll': {
        'piece': 'lemon',
    },
    'sdLemonCycleL1': {
        'piece': 'lemon',
        'level': 1,
    },
    'sdLemonCycleL2': {
        'piece': 'lemon',
        'level': 2,
    },
    'sdLemonCycleL3': {
        'piece': 'lemon',
        'level': 3,
    },
}

# Name of the team calculated upper half average cycle time data field
# to the timeline filters specified.
P75_CYCLE_DATA_FIELDS = {
    'p75OrangeCycleAll': {
        'piece': 'orange',
    },
    'p75OrangeCycleL1': {
        'piece': 'orange',
        'level': 1,
    },
    'p75OrangeCycleL2': {
        'piece': 'orange',
        'level': 2,
    },
    'p75OrangeCycleL3': {
        'piece': 'orange',
        'level': 3,
    },
    'p75LemonCycleAll': {
        'piece': 'lemon',
    },
    'p75LemonCycleL1': {
        'piece': 'lemon',
        'level': 1,
    },
    'p75LemonCycleL2': {
        'piece': 'lemon',
        'level': 2,
    },
    'p75LemonCycleL3': {
        'piece': 'lemon',
        'level': 3,
    },
}

# Name of the team calculated average cycle time data field of the last
# four matches to the timeline filters specified.
LFM_CYCLE_DATA_FIELDS = {
    'lfmOrangeCycleAll': {
        'piece': 'orange',
    },
    'lfmOrangeCycleL1': {
        'piece': 'orange',
        'level': 1,
    },
    'lfmOrangeCycleL2': {
        'piece': 'orange',
        'level': 2,
    },
    'lfmOrangeCycleL3': {
        'piece': 'orange',
        'level': 3,
    },
    'lfmLemonCycleAll': {
        'piece': 'lemon',
    },
    'lfmLemonCycleL1': {
        'piece': 'lemon',
        'level': 1,
    },
    'lfmLemonCycleL2': {
        'piece': 'lemon',
        'level': 2,
    },
    'lfmLemonCycleL3': {
        'piece': 'lemon',
        'level': 3,
    },
}

def calculate_predicted_solo_points(calculated_data):
    """Predicts the points that a team would score by themselves.

    calculated_data is the data for a team that is calculated in the
    'team_calculations()' function. Used to calculate the team's ability
    to complete each of the scoring objectives."""
    sandstorm_score = max([float(calculated_data.get('habLineSuccessL1', 0)) * 3 / 100,
                           float(calculated_data.get('habLineSuccessL2', 0)) * 6 / 100])
    # Lemons in sandstorm are worth 5 because they also score the cargo
    # they are trapping.
    lemon_score = calculated_data['avgLemonsScoredSandstorm'] * 5
    # Subtracts the lemons scored in sandstorm from the average lemons
    # scored to get the average lemons scored in teleop.
    lemon_score += (calculated_data['avgLemonsScored'] - \
        calculated_data['avgLemonsScoredSandstorm']) * 2
    orange_score = calculated_data['avgOrangesScored'] * 3
    return sandstorm_score + lemon_score + orange_score

def calculate_avg_cycle_time(cycles):
    """Calculates the average time for an action based on start and end times.

    Finds the time difference between each action pair passed and
    returns the average of the differences.

    cycles is a list of tuples where the first action in the tuple is
    the intake, and the second item is the placement or drop."""
    cycle_times = []
    for cycle in cycles:
        cycle_times.append(cycle[0].get('time') -
                           cycle[1].get('time'))
    return utils.avg(cycle_times, None)

def calculate_std_cycle_time(cycles):
    """Calculates the standard deviation time for a type of cycle.

    Finds the time difference between each action pair passed and
    returns the standard deviation of the differences.

    cycles is a list of tuples where the first action in the tuple is
    the intake, and the second item is the placement or drop."""
    cycle_times = []
    for cycle in cycles:
        cycle_times.append(cycle[0].get('time') -
                           cycle[1].get('time'))
    return sd(cycle_times)

def calculate_p75_cycle_time(cycles):
    """Calculates the upper half average time for a type of cycle.

    Finds the time difference between each action pair passed and
    returns the upper half average of the differences.

    cycles is a list of tuples where the first action in the tuple is
    the intake, and the second item is the placement or drop."""
    cycle_times = []
    for cycle in cycles:
        cycle_times.append(cycle[0].get('time') -
                           cycle[1].get('time'))
    return p75(cycle_times, cycles=True)

def p75(lis, exception=0.0, cycles=False):
    """Calculates the average of the upper half of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    cycles is whether or not the data set is cycle times. If it is, it
    takes the bottom half of the list, rather than the upper half,
    because the lower half is the faster cycle times.
    """
    # Removes the Nones from the list because if they are part of the
    # list, it returns an error.
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        # If the cycles specifcation is true, it takes the lower half of
        # the list, which are the faster cycle times.
        if cycles is True:
            # 'math.ceil()' rounds the float up to be an int.
            upper_half = lis[:math.ceil(len(lis) / 2)]
        else:
            # 'math.floor()' rounds the float down to be an int.
            upper_half = lis[-math.floor(len(lis) / 2):]
        return sum(upper_half) / len(upper_half)

def sd(lis, exception=0.0):
    """Calculates the standard deviation of a list.

    lis is the list that the standard deviation is taken of.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because if there is no data, there is no deviation.
    """
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        return np.std(lis)

def avg_percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action['didSucceed'] for action in actions]
    return round(100 * utils.avg(successes))

def sd_percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action['didSucceed'] for action in actions]
    return round(100 * sd(successes))

def p75_percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action['didSucceed'] for action in actions]
    return round(100 * p75(successes))

def filter_timeline_actions(timds, filters):
    """Puts a timeline through a filter to use for calculations.

    timds are the timds that data is calculated from.
    filters are the specifications that certain data points inside the
    timeline must fit to be included in the returned timeline. The value
    in the filter can be a tuple with the first value of the filter and
    the second value of if it is an opposite value, in which case it
    will be tested if it is not that value. The 'opposite' argument is
    optional, so if it is not a tuple, then the value will instead be
    interpreted as the requirement."""
    filtered_timeline = []
    # For each action, if any of the specifications are not met, the
    # loop breaks and it moves on to the next action, but if all the
    # specifications are met, it adds it to the filtered timeline.
    for timd in timds:
        for action in timd.get('timeline', []):
            for data_field, rough_requirement in filters.items():
                # Tests if the rough_requirement is a tuple or not. If
                # it is a tuple, the second item in the tuple is a bool
                # showing whether or not 'opposite' is True. If opposite
                # is True, it returns everything that does *not* meet
                # the specified key:value pair criteria, rather than
                # returning everything that meets the criteria.
                if type(rough_requirement) == tuple:
                    requirement = rough_requirement[0]
                    opposite = rough_requirement[1]
                else:
                    requirement = rough_requirement
                    opposite = False
                # If 'level' is not in the dictionary, it is a cargo
                # ship placement and considered to be at level 1.
                if data_field == 'level' and requirement == 1:
                    if opposite is False:
                        if action.get('level', 1) != 1:
                            break
                    else:
                        if action.get('level', 1) == 1:
                            break
                # If the filter specifies that the zone must be
                # loadingStation, it means either loading station,
                # so it only breaks if the zone is not
                # leftLoadingStation or rightLoadingStation.
                elif data_field == 'zone' and requirement == 'loadingStation':
                    if opposite is False:
                        if action['zone'] not in ['leftLoadingStation',
                                                  'rightLoadingStation']:
                            break
                    else:
                        if action['zone'] in ['leftLoadingStation',
                                              'rightLoadingStation']:
                            break
                # Otherwise, it checks the requirement normally
                else:
                    if opposite is False:
                        if action.get(data_field) != requirement:
                            break
                    else:
                        if action.get(data_field) == requirement:
                            break
            # If all the requirements are met, it adds the action to the
            # returned filtered timeline.
            else:
                filtered_timeline.append(action)
    return filtered_timeline

def filter_cycles(cycle_list, filters):
    """Puts cycles through filters to meet specific requirements.

    cycle_list is a list of tuples where the first item is an intake and
    the second action is the placement or drop. When judging the
    filters, the placement is always the one used to filter. Filters
    are only applied to placements.
    filters are the specifications that certain data points inside the
    cycles must fit to be included in the returned cycles."""
    filtered_cycles = []
    # For each cycle, if any of the specifications are not met, the
    # loop breaks and it moves on to the next cycle, but if all the
    # specifications are met, it adds it to the filtered cycles.
    for cycle in cycle_list:
        for data_field, requirement in filters.items():
            # If 'level' is not in the dictionary, it is a cargo
            # ship placement and considered to be at level 1.
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

def climb_success_rate(timds, level, string=False):
    """Calculates the success rate for climbs of a specific level.

    timds are the timds for a team.
    level is the level of climb being calculated.
    string is whether or not the success rate is returned as a string.
    If it is, it is represented in the format 'successes / attempts'."""
    climbs = filter_timeline_actions(timds, {'type': 'climb'})
    attempts = 0
    successes = 0
    for climb in climbs:
        if climb['attempted']['self'] == level:
            attempts += 1
            # 'actual' must match the 'attempt' for a climb to be
            # counted as a success
            if climb['actual']['self'] == level:
                successes += 1
    if string is True:
        if attempts == 0:
            return '0 / 0'
        return f'{successes} / {attempts}'
    else:
        if attempts == 0:
            # Returns None instead of zero because a team who didn't
            # climb at all to a specific level shouldn't have a 0%
            # success rate, becuase that implies failure.
            return None
        return round(100 * successes / attempts)

def make_paired_cycle_list(cycle_list):
    """Pairs up cycles together into tuples of intakes and outakes.

    Intakes are the first items and outakes are the second items in each
    cycle tuple.

    cycle_list is the list of actions that need to be paired up."""
    # [::2] are the even-indexed items of the list, [1::2] are the
    # odd-indexed items of the list. The python zip function puts
    # matching-index items from two lists into tuples.
    return list(zip(cycle_list[::2], cycle_list[1::2]))

def team_calculations(timds, team_number):
    """Calculates all the calculated data for one team.

    Uses a team's timds to make many calculations and return them in a
    dictionary.

    timds is the list of each match that a team has participated in."""
    calculated_data = {}

    # The list of the last four timds used for lfm (last four matches)
    # calculations.
    lfm_timds = sorted(timds, key=lambda timd: timd.get('matchNumber'))[-4:]

    # If the robot has ground intaked a piece at any point in the
    # competition, the respective hasGroundIntake data point is true.
    calculated_data['hasOrangeGroundIntake'] = True if \
        len(filter_timeline_actions(timds, {'type': 'intake', 'piece': \
        'orange', 'zone': ('loadingStation', True)})) > 0 else False
    calculated_data['hasLemonGroundIntake'] = True if \
        len(filter_timeline_actions(timds, {'type': 'intake', 'piece': \
        'orange', 'zone': ('loadingStation', True)})) > 0 else False

    # If the robot has ever preloaded the game piece type.
    calculated_data['didPreloadOrange'] = True if [
        timd for timd in timds if timd.get('preload') == 'orange'
        ] else False
    calculated_data['didPreloadLemon'] = True if [
        timd for timd in timds if timd.get('preload') == 'lemon'
        ] else False

    # Find the average of different calculated timd data points using
    # the AVERAGE_DATA_FIELDS dictionary.
    # average_data_field is the calculated team data field, and
    # timd_data_field is the respective data point in calculated
    # timd data.
    for average_data_field, timd_data_field in AVERAGE_DATA_FIELDS.items():
        calculated_data[average_data_field] = utils.avg([timd[
            'calculatedData'].get(timd_data_field) for timd in timds])

    # Calculates average defense fields similar to average data fields,
    # with the exception of only taking into account matches where the
    # team played defense.
    defending_timds = []
    for timd in timds:
        if timd['calculatedData']['timeDefending'] > 0.0:
            defending_timds.append(timd)

    calculated_data['matchesDefended'] = len(defending_timds)
    # The defense calculations should only be calculated if the team had
    # a match where they played defense.
    if calculated_data['matchesDefended'] > 0:
        calculated_data['avgFailedCyclesCaused'] = utils.avg([timd[
            'calculatedData']['totalFailedCyclesCaused'] for timd in \
            defending_timds])
        calculated_data['avgTimeDefending'] = utils.avg([timd[
            'calculatedData']['timeDefending'] for timd in \
            defending_timds])
        calculated_data['failedCyclesCaused'] = sum([timd[
            'calculatedData']['totalFailedCyclesCaused'] for timd in \
            defending_timds])
        calculated_data['totalTimeDefending'] = sum([timd[
            'calculatedData']['timeDefending'] for timd in \
            defending_timds])
        calculated_data['failedCyclesCausedPerSecond'] = calculated_data[
            'failedCyclesCaused'] / calculated_data['totalTimeDefending']

    # Calculations for percent successes for different actions using the
    # SUCCESS_DATA_FIELDS dictionary.
    for success_data_field, filters_ in SUCCESS_DATA_FIELDS.items():
        calculated_data[success_data_field] = avg_percent_success(
            filter_timeline_actions(timds, filters_))

    # 'hab_level_one' and 'hab_level_two' are lists of booleans
    hab_level_one = [timd['crossedHabLine'] for timd in timds if
                     timd.get('startingLevel') == 1]
    hab_level_two = [timd['crossedHabLine'] for timd in timds if
                     timd.get('startingLevel') == 2]

    # Percentages and fractions of hab line successes.
    # Only calculates hab level success if they attempted to cross from
    # that level.
    if hab_level_one != []:
        calculated_data['habLineSuccessL1'] = round(100 * utils.avg(hab_level_one))
    if hab_level_two != []:
        calculated_data['habLineSuccessL2'] = round(100 * utils.avg(hab_level_two))
    calculated_data['habLineAttemptsL1'] = f'{sum(hab_level_one)} / {len(hab_level_one)}'
    calculated_data['habLineAttemptsL2'] = f'{sum(hab_level_two)} / {len(hab_level_two)}'

    # Averages of super data points in timd.
    calculated_data['avgAgility'] = utils.avg([
        timd.get('rankAgility') for timd in timds])
    calculated_data['avgSpeed'] = utils.avg([
        timd.get('rankSpeed') for timd in timds])

    # TIMDs where the team resisted defense
    resisted_timds = []
    for timd in timds:
        if timd.get('rankResistance', 0) != 0:
            resisted_timds.append(timd)

    calculated_data['avgResistance'] = utils.avg([
        timd.get('rankResistance') for timd in resisted_timds], None)

    # When calculating the super average for defense, takes out the
    # matches when they didn't play defense (matches where rankDefense
    # is 0).
    defending_matches = []
    for timd in timds:
        if timd.get('rankDefense') != 0:
            defending_matches.append(timd)

    # If a team didn't play defense, they shouldn't have a 0 for their
    # defense rank, because it is undetermined.
    calculated_data['avgRankDefense'] = utils.avg([
        timd.get('rankDefense') for timd in defending_matches], None)

    # Takes out the matches when they didn't play counter defense
    # (matches where rankCounterDefense is 0).
    counter_defending_matches = []
    for timd in timds:
        if timd.get('rankCounterDefense') != 0:
            counter_defending_matches.append(timd)

    points_prevented_matches = []
    for timd in timds:
        if timd['calculatedData'].get('pointsPrevented', 0) > 0:
            points_prevented_matches.append(timd)

    calculated_data['avgPointsPrevented'] = avg([
        timd['calculatedData'].get('pointsPrevented') for timd in points_prevented_matches], None)
    calculated_data['avgOrangePointsPrevented'] = avg([
        timd['calculatedData'].get('orangePointsPrevented') for timd in points_prevented_matches], None)
    calculated_data['avgLemonPointsPrevented'] = avg([
        timd['calculatedData'].get('lemonPointsPrevented') for timd in points_prevented_matches], None)

    # If a team didn't play defense, they shouldn't have a 0 for their
    # counter defense rank, because it is undetermined.
    calculated_data['avgRankCounterDefense'] = utils.avg([
        timd.get('rankCounterDefense') for timd in counter_defending_matches], None)

    # Percent of matches of incap, no-show, or dysfunctional
    matches_incap = [True if timd['calculatedData']['timeIncap'] > 0.0
                     else False for timd in timds]
    matches_no_show = [timd.get('isNoShow') for timd in timds]
    calculated_data['percentIncap'] = round(100 * utils.avg(matches_incap))
    calculated_data['percentNoShow'] = round(100 * utils.avg(matches_no_show))
    # 'percentDysfunctional' is the percent of matches a team is incap
    # or no-show.
    calculated_data['percentDysfunctional'] = round(100 * utils.avg([
        incap or no_show for incap, no_show in zip(matches_incap,
                                                   matches_no_show)]))
    calculated_data['percentIncapEntireMatch'] = round(100 * utils.avg([
        timd['calculatedData'].get('isIncapEntireMatch') for timd in
        timds]))

    # Repeats all the previous calculations for only the last four timds.
    # lfm_average_data_field is the calculated team data field, and
    # timd_data_field is the respective data point in calculated
    # timd data.
    for lfm_average_data_field, timd_data_field in LFM_AVERAGE_DATA_FIELDS.items():
        calculated_data[lfm_average_data_field] = utils.avg([
            timd['calculatedData'].get(timd_data_field) for timd in
            lfm_timds])

    for lfm_success_data_field, filters_ in LFM_SUCCESS_DATA_FIELDS.items():
        calculated_data[lfm_success_data_field] = avg_percent_success(
            filter_timeline_actions(lfm_timds, filters_))

    calculated_data['lfmHabLineSuccessL1'] = round(100 * utils.avg([
        timd['crossedHabLine'] for timd in lfm_timds if
        timd.get('startingLevel') == 1]))
    calculated_data['lfmHabLineSuccessL2'] = round(100 * utils.avg([
        timd['crossedHabLine'] for timd in lfm_timds if
        timd.get('startingLevel') == 2]))

    climbs = filter_timeline_actions(timds, {'type': 'climb'})
    for level in [1, 2, 3]:
        level_attempts = len([climb for climb in climbs if \
                              climb['attempted']['self'] == level])
        if level_attempts > 0:
            calculated_data[f'climbSuccessL{level}'] = \
                climb_success_rate(timds, level)

    calculated_data['climbAttemptsL1'] = climb_success_rate(timds, 1, \
        string=True)
    calculated_data['climbAttemptsL2'] = climb_success_rate(timds, 2, \
        string=True)
    calculated_data['climbAttemptsL3'] = climb_success_rate(timds, 3, \
        string=True)

    calculated_data['lfmPercentIncap'] = round(100 * utils.avg([
        True if timd['calculatedData']['timeIncap'] > 0.0 else
        False for timd in lfm_timds]))
    calculated_data['lfmPercentNoShow'] = round(100 * utils.avg([
        timd.get('isNoShow') for timd in lfm_timds]))
    calculated_data['lfmPercentIncapEntireMatch'] = round(100 * utils.avg([
        timd['calculatedData'].get('isIncapEntireMatch') for timd in
        lfm_timds]))

    # Finds the standard deviations of all the previous average data
    # fields.
    # sd_data_field is the calculated team data field, and
    # timd_data_field is the respective data point in calculated
    # timd data.
    # TODO: Change name of 'sdAvg...' data fields to 'sd...' data fields
    for sd_data_field, timd_data_field in SD_DATA_FIELDS.items():
        calculated_data[sd_data_field] = sd([
            timd['calculatedData'].get(timd_data_field) for timd in
            timds])

    # Finds the upper half average of all the previously calculated data
    # points.
    # p75_average_data_field is the calculated team data field, and
    # timd_data_field is the respective data point in calculated
    # timd data.
    for p75_average_data_field, timd_data_field in P75_DATA_FIELDS.items():
        calculated_data[p75_average_data_field] = p75([
            timd['calculatedData'].get(timd_data_field) for timd in
            timds])

    # Takes out all the cycles in all the timds for a team. These will
    # be used for average cycle time calculations.
    total_cycle_list = []
    for cycle_timd in timds:
        cycle_list = []
        for action in cycle_timd.get('timeline', []):
            if action['type'] in ['intake', 'placement', 'type']:
                cycle_list.append(action)
        # There must be at least 2 actions to have a cycle.
        if len(cycle_list) > 1:
            # If the first action in the list is a placement, it is a
            # preload, which doesn't count when calculating cycle times.
            if cycle_list[0].get('type') == 'placement':
                cycle_list.pop(0)
            # If the last action in the list is an intake, it means the
            # robot finished with a game object, in which the cycle was
            # never completed.
            if cycle_list[-1].get('type') == 'intake':
                cycle_list.pop(-1)
            paired_cycle_list = make_paired_cycle_list(cycle_list)
            total_cycle_list += paired_cycle_list

    # Calculates the average cycle time for each cycle type.
    for cycle_data_field, filters_ in CYCLE_DATA_FIELDS.items():
        calculated_data[cycle_data_field] = calculate_avg_cycle_time(
            filter_cycles(total_cycle_list, filters_))

    # Calculates the standard deviation cycle time for each cycle type.
    for sd_cycle_data_field, filters_ in SD_CYCLE_DATA_FIELDS.items():
        calculated_data[sd_cycle_data_field] = calculate_std_cycle_time(
            filter_cycles(total_cycle_list, filters_))

    # Finds the upper half average of each type of cycle.
    for p75_cycle_data_field, filters_ in P75_CYCLE_DATA_FIELDS.items():
        calculated_data[p75_cycle_data_field] = \
            calculate_p75_cycle_time(filter_cycles(total_cycle_list, \
            filters_))

    # Repeats the process of gathering cycles for a team, except limited
    # to only the last four matches.
    lfm_cycle_list = []
    for cycle_timd in lfm_timds:
        cycle_list = []
        for action in cycle_timd.get('timeline', []):
            if action['type'] in ['intake', 'placement', 'type']:
                cycle_list.append(action)
        # There must be at least 2 actions to have a cycle.
        if len(cycle_list) > 1:
            # If the first action in the list is a placement, it is a
            # preload, which doesn't count when calculating cycle times.
            if cycle_list[0].get('type') == 'placement':
                cycle_list.pop(0)
            # If the last action in the list is an intake, it means the
            # robot finished with a game object, in which the cycle was
            # never completed.
            if cycle_list[-1].get('type') == 'intake':
                cycle_list.pop(-1)
            paired_cycle_list = make_paired_cycle_list(cycle_list)
            lfm_cycle_list += paired_cycle_list

    # Calculates the last four match average for each cycle type.
    for lfm_cycle_data_field, filters_ in LFM_CYCLE_DATA_FIELDS.items():
        calculated_data[lfm_cycle_data_field] = \
            calculate_avg_cycle_time(filter_cycles(lfm_cycle_list, \
            filters_))

    # 'lastMatch' is the team's last match when team data is calculated.
    # Used in the viewer to display when a team's data was last updated.
    if timds != []:
        calculated_data['lastMatch'] = max([timd['matchNumber'] for timd in timds])

    # Calculates predicted solo points based on the team's proficiency
    # in all the scoring objectives in the game.
    calculated_data['predictedSoloPoints'] = \
        calculate_predicted_solo_points(calculated_data)

    return calculated_data

# Check to ensure Team number is being passed as an argument
if len(sys.argv) == 2:
    # Extract Team number from system argument
    # Team number is a string
    TEAM_NUMBER = sys.argv[1]
else:
    print('Error: Team number not being passed as an argument. Exiting...')
    sys.exit(0)

# Uses the team number to find all the TIMDs for the passed team.
TIMDS = []
for timd in os.listdir(utils.create_file_path('data/cache/timds')):
    if timd.split('Q')[0] == TEAM_NUMBER:
        with open(utils.create_file_path(
                f'data/cache/timds/{timd}')) as timd_file:
            timd_data = json.load(timd_file)
        # If there is no calculatedData in the timd, it hasn't been
        # calculated yet, so it shouldn't be used in calculations.
        if timd_data.get('calculatedData') is not None:
            TIMDS.append(timd_data)

FINAL_TEAM_DATA = {'calculatedData': team_calculations(TIMDS, TEAM_NUMBER)}

# Save data in local cache
with open(utils.create_file_path(
        f'data/cache/teams/{TEAM_NUMBER}.json'), 'w') as file:
    json.dump(FINAL_TEAM_DATA, file)

# Save data in Firebase upload queue
with open(utils.create_file_path(
        f'data/upload_queue/teams/{TEAM_NUMBER}.json'), 'w') as file:
    json.dump(FINAL_TEAM_DATA, file)
