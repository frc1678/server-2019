#!/usr/bin/python3.6
"""Calculations for a single Team.

Team calculations include the calculation of data points that are
reflective of a team's performance across all of their matches.

Called by server.py with the number of the Team to be calculated."""
# External imports
import json
import os
import sys
import numpy as np
# Internal imports
import utils

def first_pick_ability(calculated_data):
    """Calculates the relative first pick score for a team.

    calculated_data is the dictionary of data calculated for a team."""
    #TODO: Implement first pick calculations once strategy decides
    return 0.0

def second_pick_ability(calculated_data):
    """Calculates the relative second pick score for a team.

    calculated_data is the dictionary of data calculated for a team."""
    #TODO: Implement second pick calculations once strategy decides
    return 0.0

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
    return avg(cycle_times, None)

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
    return np.std(cycle_times)

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
    return p75(cycle_times)

def p75(lis, exception=0.0):
    """Calculates the average of the upper half of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    if len(lis) == 0:
        return exception
    else:
        upper_half = lis[-(round(len(lis) / 2)):]
        return sum(upper_half) / len(upper_half)

def avg(lis, exception=0.0):
    """Calculates the average of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    if len(lis) == 0:
        return exception
    else:
        return sum(lis) / len(lis)

def avg_percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action.get('didSucceed') for action in actions]
    return round(100 * avg(successes))

def sd_percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action.get('didSucceed') for action in actions]
    return round(100 * np.std(successes))

def p75_percent_success(actions):
    """Finds the percent of times didSucceed is true in a list of actions.

    actions is the list of actions that can either succeed or fail."""
    successes = [action.get('didSucceed') for action in actions]
    return round(100 * p75(successes))

def filter_timeline_actions(timds, **filters):
    """Puts a timeline through a filter to use for calculations.
    
    timds are the timds that data is calculated from.
    filters are the specifications that certain data points inside the
    timeline must fit to be included in the returned timeline. The value
    in the filter can be a tuple with the first value of the filter and the
    second value of if it is an opposite value, in which case it will be
    tested if it is not that value. If it is not a tuple, then the value
    will instead be interpreted as the requirement."""
    filtered_timeline = []
    # For each action, if any of the specifications are not met, the
    # loop breaks and it moves on to the next action, but if all the
    # specifications are met, it adds it to the filtered timeline.
    for timd in timds:
        for action in timd.get('timeline', []):
            for data_field, rough_requirement in filters.items():
                # Tests if the rough_requirement is a tuple or not. If
                # it is a tuple, the second item in the tuple is a bool
                # showing whether or not opposite is True. If opposite
                # is True, it validates that the specification is not
                # met, rather than is met.
                if type(rough_requirement) == tuple:
                    requirement = rough_requirement[0]
                    opposite = rough_requirement[1]
                else:
                    requirement = rough_requirement
                    opposite = False
                # If the data_field requirement is level 1, it instead
                # checks for it not being level 2 or 3, because level 1
                # can encompass all non-level 2 or 3 placement.
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

def filter_cycles(cycle_list, **filters):
    """Puts cycles through filters to meet specific requirements.

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

def make_paired_cycle_list(cycle_list):
    """Pairs up cycles together into tuples.

    cycle_list is the list of actions that need to be paired up."""
    # [::2] are the even-indexed items of the list, [1::2] are the
    # odd-indexed items of the list. The python zip function puts
    # matching-index items from two lists into tuples.
    return list(zip(cycle_list[::2], cycle_list[1::2]))

def team_calculations(timds):
    """Calculates all the calculated data for one team.

    Uses a team's timds to make many calculations and return them in a
    dictionary of calculatedData, the same that is used when exporting
    to the firebase later on.

    timds is the list of timds that a team has participated in, this is
    where the data comes from when making calculations."""
    calculated_data = {}

    # The list of the last four timds used for lfm calculations.
    lfm_timds = sorted(timds, key=lambda timd: timd.get('matchNumber'))[-4:]

    # If the robot has ground intaked a piece at any point in the
    # competition, the respective hasGroundIntake data point is true.
    calculated_data['hasOrangeGroundIntake'] = True if \
        filter_timeline_actions(timds, type='intake', piece='orange', \
        zone=('loadingStation', True)) else False
    calculated_data['hasLemonGroundIntake'] = True if \
        filter_timeline_actions(timds, type='intake', piece='lemon', \
        zone=('loadingStation', True)) else False

    # If the robot has ever preloaded each game piece type.
    calculated_data['didPreloadOrange'] = True if [
        timd for timd in timds if timd.get('preload') == 'orange'
        ] else False
    calculated_data['didPreloadLemon'] = True if [
        timd for timd in timds if timd.get('preload') == 'lemon'
        ] else False

    # Find the average of different calculated timd data points.
    calculated_data['avgOrangesScored'] = avg([timd[
        'calculatedData'].get('orangesScored') for timd in timds])
    calculated_data['avgLemonsScored'] = avg([timd[
        'calculatedData'].get('lemonsScored') for timd in timds])
    calculated_data['avgOrangesFouls'] = avg([timd[
        'calculatedData'].get('orangeFouls') for timd in timds])
    calculated_data['avgLemonsSpilled'] = avg([timd[
        'calculatedData'].get('lemonsSpilled') for timd in timds])
    calculated_data['avgOrangesScoredSandstorm'] = avg([timd[
        'calculatedData'].get('orangesScoredSandstorm') for timd in timds])
    calculated_data['avgLemonsScoredSandstorm'] = avg([timd[
        'calculatedData'].get('lemonsScoredSandstorm') for timd in timds])
    calculated_data['avgOrangesScoredTeleL1'] = avg([timd[
        'calculatedData'].get('orangesScoredTeleL1') for timd in timds])
    calculated_data['avgOrangesScoredTeleL2'] = avg([timd[
        'calculatedData'].get('orangesScoredTeleL2') for timd in timds])
    calculated_data['avgOrangesScoredTeleL3'] = avg([timd[
        'calculatedData'].get('orangesScoredTeleL3') for timd in timds])
    calculated_data['avgLemonsScoredTeleL1'] = avg([timd[
        'calculatedData'].get('lemonsScoredTeleL1') for timd in timds])
    calculated_data['avgLemonsScoredTeleL2'] = avg([timd[
        'calculatedData'].get('lemonsScoredTeleL2') for timd in timds])
    calculated_data['avgLemonsScoredTeleL3'] = avg([timd[
        'calculatedData'].get('lemonsScoredTeleL3') for timd in timds])

    # Calculations for percent successes for different actions.
    calculated_data['lemonLoadSuccess'] = avg_percent_success(
        filter_timeline_actions(timds, type='intake', piece='lemon', \
        zone='leftLoadingStation'))
    calculated_data['orangeSuccessAll'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange'))
    calculated_data['orangeSuccessDefended'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', wasDefended='True'))
    calculated_data['orangeSuccessUndefended'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', wasDefended='False'))
    calculated_data['orangeSuccessL1'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=1))
    calculated_data['orangeSuccessL2'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=2))
    calculated_data['orangeSuccessL3'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=3))
    calculated_data['lemonSuccessAll'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon'))
    calculated_data['lemonSuccessDefended'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', wasDefended='True'))
    calculated_data['lemonSuccessUndefended'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', wasDefended='False'))
    calculated_data['lemonSuccessL1'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=1))
    calculated_data['lemonSuccessL2'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=2))
    calculated_data['lemonSuccessL3'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=3))
    calculated_data['lemonSuccessFromSide'] = avg_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', side=('near', True)))
    calculated_data['habLineSuccessL1'] = round(100 * avg([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 1]))
    calculated_data['habLineSuccessL2'] = round(100 * avg([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 2]))

    # Averages of super data points in timd.
    calculated_data['avgGoodDecisions'] = avg([
        timd.get('numGoodDecisions') for timd in timds])
    calculated_data['avgBadDecisions'] = avg([
        timd.get('numBadDecisions') for timd in timds])

    # Finds the averages of different calculated times in timds.
    calculated_data['avgTimeIncap'] = avg([
        timd['calculatedData'].get('timeIncap') for timd in timds])
    calculated_data['avgTimeImpaired'] = avg([
        timd['calculatedData'].get('timeImpaired') for timd in timds])
    calculated_data['avgTimeClimbing'] = avg([
        timd['calculatedData'].get('timeClimbing') for timd in timds])

    # Finds the percent of matches a team was incap, impaired, and no show.
    calculated_data['percentIncap'] = round(100 * avg([
        True if timd['calculatedData'].get('timeIncap') > 0.0 else
        False for timd in timds]))
    calculated_data['percentImpaired'] = round(100 * avg([
        True if timd['calculatedData'].get('timeImpaired') > 0.0 else
        False for timd in timds]))
    calculated_data['percentNoShow'] = round(100 * avg([
        timd.get('isNoShow') for timd in timds]))
    calculated_data['percentIncapEntireMatch'] = round(100 * avg([
        timd['calculatedData'].get('isIncapEntireMatch') for timd in
        timds]))

    # Repeats all the previous calculations for only the last four timds.
    calculated_data['lfmAvgOrangesScored'] = avg([
        timd['calculatedData'].get('orangesScored') for timd in
        lfm_timds])
    calculated_data['lfmAvgLemonsScored'] = avg([
        timd['calculatedData'].get('lemonsScored') for timd in
        lfm_timds])
    calculated_data['lfmAvgOrangesFouls'] = avg([
        timd['calculatedData'].get('orangeFouls') for timd in
        lfm_timds])
    calculated_data['lfmAvgLemonsSpilled'] = avg([
        timd['calculatedData'].get('lemonsSpilled') for timd in
        lfm_timds])

    calculated_data['lfmLemonLoadSuccess'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='intake', \
        piece='lemon', zone='loadingStation'))
    calculated_data['lfmOrangeSuccessAll'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='orange'))
    calculated_data['lfmOrangeSuccessDefended'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='orange', wasDefended=True))
    calculated_data['lfmOrangeSuccessUndefended'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='orange', wasDefended=False))
    calculated_data['lfmOrangeSuccessL1'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='orange', level=1))
    calculated_data['lfmOrangeSuccessL2'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='orange', level=2))
    calculated_data['lfmOrangeSuccessL3'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='orange', level=3))
    calculated_data['lfmLemonSuccessAll'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='lemon'))
    calculated_data['lfmLemonSuccessDefended'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='lemon', wasDefended=True))
    calculated_data['lfmLemonSuccessUndefended'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='lemon', wasDefended=False))
    calculated_data['lfmLemonSuccessL1'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='lemon', level=1))
    calculated_data['lfmLemonSuccessL2'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='lemon', level=2))
    calculated_data['lfmLemonSuccessL3'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='lemon', level=3))
    calculated_data['lfmLemonSuccessFromSide'] = avg_percent_success(
        filter_timeline_actions(lfm_timds, type='placement', \
        piece='lemon', side=('near', True)))
    calculated_data['lfmHabLineSuccessL1'] = round(100 * avg([
        timd['crossedHabLine'] for timd in lfm_timds if
        timd.get('startingLevel') == 1]))
    calculated_data['lfmHabLineSuccessL2'] = round(100 * avg([
        timd['crossedHabLine'] for timd in lfm_timds if
        timd.get('startingLevel') == 2]))

    calculated_data['lfmAvgGoodDecisions'] = avg([
        timd.get('numGoodDecisions') for timd in lfm_timds])
    calculated_data['lfmAvgBadDecisions'] = avg([
        timd.get('numBadDecisions') for timd in lfm_timds])

    calculated_data['lfmAvgTimeIncap'] = avg([
        timd['calculatedData'].get('timeIncap') for timd in
        lfm_timds])
    calculated_data['lfmAvgTimeImpaired'] = avg([
        timd['calculatedData'].get('timeImpaired') for timd in
        lfm_timds])
    calculated_data['lfmAvgTimeClimbing'] = avg([
        timd['calculatedData'].get('timeClimbing') for timd in
        lfm_timds])

    calculated_data['lfmPercentIncap'] = round(100 * avg([
        True if timd['calculatedData'].get('timeIncap') > 0.0 else
        False for timd in lfm_timds]))
    calculated_data['lfmPercentImpaired'] = round(100 * avg([
        True if timd['calculatedData'].get('timeImpaired') > 0.0 else
        False for timd in lfm_timds]))
    calculated_data['lfmPercentNoShow'] = round(100 * avg([
        timd.get('isNoShow') for timd in lfm_timds]))
    calculated_data['lfmPercentIncapEntireMatch'] = round(100 * avg([
        timd['calculatedData'].get('isIncapEntireMatch') for timd in
        lfm_timds]))

    # Finds the standard deviations of all the previous calculations
    # instead of averages.
    calculated_data['sdAvgOrangesScored'] = np.std([
        timd['calculatedData'].get('orangesScored') for timd in timds])
    calculated_data['sdAvgLemonsScored'] = np.std([
        timd['calculatedData'].get('lemonsScored') for timd in timds])
    calculated_data['sdAvgOrangesFouls'] = np.std([
        timd['calculatedData'].get('orangeFouls') for timd in timds])
    calculated_data['sdAvgLemonsSpilled'] = np.std([
        timd['calculatedData'].get('lemonsSpilled') for timd in timds])

    calculated_data['sdLemonLoadSuccess'] = sd_percent_success(
        filter_timeline_actions(timds, type='intake', piece='lemon', \
        zone='loadingStation'))
    calculated_data['sdOrangeSuccessAll'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange'))
    calculated_data['sdOrangeSuccessDefended'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', wasDefended=True))
    calculated_data['sdOrangeSuccessUndefended'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', wasDefended=False))
    calculated_data['sdOrangeSuccessL1'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=1))
    calculated_data['sdOrangeSuccessL2'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=2))
    calculated_data['sdOrangeSuccessL3'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=3))
    calculated_data['sdLemonSuccessAll'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon'))
    calculated_data['sdLemonSuccessDefended'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', wasDefended=True))
    calculated_data['sdLemonSuccessUndefended'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', wasDefended=False))
    calculated_data['sdLemonSuccessL1'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=1))
    calculated_data['sdLemonSuccessL2'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=2))
    calculated_data['sdLemonSuccessL3'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=3))
    calculated_data['sdLemonSuccessFromSide'] = sd_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', side=('near', True)))
    calculated_data['sdHabLineSuccessL1'] = round(100 * np.std([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 1]))
    calculated_data['sdHabLineSuccessL2'] = round(100 * np.std([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 2]))

    calculated_data['sdAvgGoodDecisions'] = np.std([
        timd.get('numGoodDecisions') for timd in timds])
    calculated_data['sdAvgBadDecisions'] = np.std([
        timd.get('numBadDecisions') for timd in timds])

    calculated_data['sdAvgTimeIncap'] = np.std([
        timd['calculatedData'].get('timeIncap') for timd in timds])
    calculated_data['sdAvgTimeImpaired'] = np.std([
        timd['calculatedData'].get('timeImpaired') for timd in timds])
    calculated_data['sdAvgTimeClimbing'] = np.std([
        timd['calculatedData'].get('timeClimbing') for timd in timds])

    calculated_data['sdPercentIncap'] = round(100 * np.std([
        True if timd['calculatedData'].get('timeIncap') > 0.0 else
        False for timd in timds]))
    calculated_data['sdPercentImpaired'] = round(100 * np.std([
        True if timd['calculatedData'].get('timeImpaired') > 0.0 else
        False for timd in timds]))
    calculated_data['sdPercentNoShow'] = round(100 * np.std([
        timd.get('isNoShow') for timd in timds]))
    calculated_data['sdPercentIncapEntireMatch'] = round(100 * np.std([
        timd['calculatedData'].get('isIncapEntireMatch') for timd in
        timds]))

    # Finds the upper half average of all the previously calculated data
    # points.
    calculated_data['p75AvgOrangesScored'] = p75([
        timd['calculatedData'].get('orangesScored') for timd in timds])
    calculated_data['p75AvgLemonsScored'] = p75([
        timd['calculatedData'].get('lemonsScored') for timd in timds])
    calculated_data['p75AvgOrangesFouls'] = p75([
        timd['calculatedData'].get('orangeFouls') for timd in timds])
    calculated_data['p75AvgLemonsSpilled'] = p75([
        timd['calculatedData'].get('lemonsSpilled') for timd in timds])

    calculated_data['p75LemonLoadSuccess'] = p75_percent_success(
        filter_timeline_actions(timds, type='intake', piece='lemon', \
        zone='loadingStation'))
    calculated_data['p75OrangeSuccessAll'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange'))
    calculated_data['p75OrangeSuccessDefended'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', wasDefended=True))
    calculated_data['p75OrangeSuccessUndefended'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', wasDefended=False))
    calculated_data['p75OrangeSuccessL1'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=1))
    calculated_data['p75OrangeSuccessL2'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=2))
    calculated_data['p75OrangeSuccessL3'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='orange', level=3))
    calculated_data['p75LemonSuccessAll'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon'))
    calculated_data['p75LemonSuccessDefended'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', wasDefended=True))
    calculated_data['p75LemonSuccessUndefended'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', wasDefended=False))
    calculated_data['p75LemonSuccessL1'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=1))
    calculated_data['p75LemonSuccessL2'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=2))
    calculated_data['p75LemonSuccessL3'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', level=3))
    calculated_data['p75LemonSuccessFromSide'] = p75_percent_success(
        filter_timeline_actions(timds, type='placement', \
        piece='lemon', side=('near', True)))
    calculated_data['p75HabLineSuccessL1'] = round(100 * p75([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 1]))
    calculated_data['p75HabLineSuccessL2'] = round(100 * p75([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 2]))

    calculated_data['p75AvgGoodDecisions'] = p75([
        timd.get('numGoodDecisions') for timd in timds])
    calculated_data['p75AvgBadDecisions'] = p75([
        timd.get('numBadDecisions') for timd in timds])

    calculated_data['p75AvgTimeIncap'] = p75([
        timd['calculatedData'].get('timeIncap') for timd in timds])
    calculated_data['p75AvgTimeImpaired'] = p75([
        timd['calculatedData'].get('timeImpaired') for timd in timds])
    calculated_data['p75AvgTimeClimbing'] = p75([
        timd['calculatedData'].get('timeClimbing') for timd in timds])

    calculated_data['p75PercentIncap'] = round(100 * p75([
        True if timd['calculatedData'].get('timeIncap') > 0.0 else
        False for timd in timds]))
    calculated_data['p75PercentImpaired'] = round(100 * p75([
        True if timd['calculatedData'].get('timeImpaired') > 0.0 else
        False for timd in timds]))
    calculated_data['p75PercentNoShow'] = round(100 * p75([
        timd.get('isNoShow') for timd in timds]))
    calculated_data['p75PercentIncapEntireMatch'] = round(100 * p75([
        timd['calculatedData'].get('isIncapEntireMatch') for timd in
        timds]))

    # Takes out all the cycles in all the timds for a team. These will
    # be used for average cycle time calculations.
    total_cycle_list = []
    for cycle_timd in timds:
        cycle_list = []
        for action in cycle_timd.get('timeline'):
            if action['type'] in ['intake', 'placement', 'type']:
                cycle_list.append(action)
        if len(cycle_list) > 0:
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
    calculated_data['orangeCycleAll'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='orange'))
    calculated_data['orangeCycleL1'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=1))
    calculated_data['orangeCycleL2'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=2))
    calculated_data['orangeCycleL3'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=3))
    calculated_data['lemonCycleAll'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon'))
    calculated_data['lemonCycleL1'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=1))
    calculated_data['lemonCycleL2'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=2))
    calculated_data['lemonCycleL3'] = calculate_avg_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=3))

    # Calculates the standard deviation cycle time for each cycle type.
    calculated_data['sdOrangeCycleAll'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='orange'))
    calculated_data['sdOrangeCycleL1'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=1))
    calculated_data['sdOrangeCycleL2'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=2))
    calculated_data['sdOrangeCycleL3'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=3))
    calculated_data['sdLemonCycleAll'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon'))
    calculated_data['sdLemonCycleL1'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=1))
    calculated_data['sdLemonCycleL2'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=2))
    calculated_data['sdLemonCycleL3'] = calculate_std_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=3))

    # Finds the upper half average of each type of cycle.
    calculated_data['p75OrangeCycleAll'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='orange'))
    calculated_data['p75OrangeCycleL1'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=1))
    calculated_data['p75OrangeCycleL2'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=2))
    calculated_data['p75OrangeCycleL3'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='orange', level=3))
    calculated_data['p75LemonCycleAll'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon'))
    calculated_data['p75LemonCycleL1'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=1))
    calculated_data['p75LemonCycleL2'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=2))
    calculated_data['p75LemonCycleL3'] = calculate_p75_cycle_time(
        filter_cycles(total_cycle_list, piece='lemon', level=3))

    # Repeats the process of gathering cycles for a team, except limited
    # to only the last four matches.
    lfm_cycle_list = []
    for cycle_timd in lfm_timds:
        cycle_list = []
        for action in cycle_timd.get('timeline'):
            if action['type'] in ['intake', 'placement', 'type']:
                cycle_list.append(action)
        if len(cycle_list) > 0:
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
    calculated_data['lfmOrangeCycleAll'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='orange'))
    calculated_data['lfmOrangeCycleL1'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='orange', level=1))
    calculated_data['lfmOrangeCycleL2'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='orange', level=2))
    calculated_data['lfmOrangeCycleL3'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='orange', level=3))
    calculated_data['lfmLemonCycleAll'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='lemon'))
    calculated_data['lfmLemonCycleL1'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='lemon', level=1))
    calculated_data['lfmLemonCycleL2'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='lemon', level=2))
    calculated_data['lfmLemonCycleL3'] = calculate_avg_cycle_time(
        filter_cycles(lfm_cycle_list, piece='lemon', level=3))

    # Calculates the first and second pick ability for the team based on
    # their previous calculated data. To see how these are calculated,
    # look at the weights in each of their respective functions.
    calculated_data['firstPickAbility'] = \
        first_pick_ability(calculated_data)
    calculated_data['secondPickAbility'] = \
        second_pick_ability(calculated_data)

    return calculated_data

# Check to ensure Team number is being passed as an argument
if len(sys.argv) == 2:
    # Extract Team number from system argument
    TEAM_NUMBER = int(sys.argv[1])
else:
    print('Error: Team number not being passed as an argument. Exiting...')
    sys.exit(0)

# Uses the team number to find all the TIMDs for the passed team.
TIMDS = []
for timd in os.listdir(utils.create_file_path('data/cache/timds')):
    if TEAM_NUMBER in timd:
        with open(utils.create_file_path(
                f'data/cache/timds/{timd}')) as timd_file:
            TIMDS.append(timd_file.read())

FINAL_TEAM_DATA = {'calculatedData': team_calculations(TIMDS)}

# Save data in local cache
with open(utils.create_file_path(f'data/teams/{TEAM_NUMBER}.json'),
          'w') as file:
    json.dump(FINAL_TEAM_DATA, file)

# Save data in Firebase upload queue
with open(utils.create_file_path(
        f'data/upload_queue/teams/{TEAM_NUMBER}.json'), 'w') as file:
    json.dump(FINAL_TEAM_DATA, file)
