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

# Check to ensure Team number is being passed as an argument
if len(sys.argv) == 2:
    # Extract Team number from system argument
    TEAM_NUMBER = int(sys.argv[1])
else:
    print('Error: Team number not being passed as an argument. Exiting...')
    sys.exit(0)

def p75(lis, exception=0.0):
    """Calculates the average of the upper half of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    try:
        upper_half = lis[-(round(len(lis) / 2)):]
        return sum(upper_half) / len(upper_half)
    except (ZeroDivisionError, TypeError):
        return exception

def avg(lis, exception=0.0):
    """Calculates the average of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    try:
        return sum(lis) / len(lis)
    except (ZeroDivisionError, TypeError):
        return exception

def team_calculations(timds):
    """Calculates all the calculated data for one team.

    Uses a team's timds to make many calculations and return them in a
    dictionary of calculatedData, the same that is used when exporting
    to the firebase later on.
    timds is the list of timds that a team has participated in, this is
    where the data comes from when making calculations."""
    calculated_data = {}

    lfm_timds = sorted(timds, key=lambda timd: timd.get('matchNumber'))[-4:]

    calculated_data['hasOrangeGroundIntake'] = True if [
        action for timd in timds for action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'orange' and
        action.get('zone') != 'leftLoadingStation' and
        action.get('zone') != 'rightLoadingStation'] else False
    calculated_data['hasOrangeGroundIntake'] = True if [
        action for timd in timds for action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'lemon' and
        action.get('zone') != 'leftLoadingStation' and
        action.get('zone') != 'rightLoadingStation'] else False

    calculated_data['didPreloadOrange'] = True if [
        timd for timd in timds if timd.get('preload') == 'orange'
        ] else False
    calculated_data['didPreloadLemon'] = True if [
        timd for timd in timds if timd.get('preload') == 'lemon'
        ] else False

    calculated_data['avgOrangesScored'] = avg([
        timd['calculatedData'].get('orangesScored') for timd in timds])
    calculated_data['avgLemonsScored'] = avg([
        timd['calculatedData'].get('lemonsScored') for timd in timds])
    calculated_data['avgOrangesFouls'] = avg([
        timd['calculatedData'].get('orangeFouls') for timd in timds])
    calculated_data['avgLemonsSpilled'] = avg([
        timd['calculatedData'].get('lemonsSpilled') for timd in timds])

    calculated_data['lemonLoadSuccess'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'lemon' and
        (action.get('zone') == 'leftLoadingStation' or
         action.get('zone') == 'leftLoadingStation')]))

    calculated_data['orangeSuccessAll'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange']))
    calculated_data['orangeSuccessDefended'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is True]))
    calculated_data['orangeSuccessUndefended'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is False]))
    calculated_data['orangeSuccessL1'] = round(100.0 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['orangeSuccessL2'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 2]))
    calculated_data['orangeSuccessL3'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 3]))

    calculated_data['lemonSuccessAll'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon']))
    calculated_data['lemonSuccessDefended'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is True]))
    calculated_data['lemonSuccessUndefended'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is False]))
    calculated_data['lemonSuccessL1'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['lemonSuccessL2'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 2]))
    calculated_data['lemonSuccessL3'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 3]))
    calculated_data['lemonSuccessFromSide'] = round(100 * avg([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('side') != 'near']))

    calculated_data['habLineSuccessL1'] = round(100 * avg([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 1]))
    calculated_data['habLineSuccessL2'] = round(100 * avg([
        timd['crossedHabLine'] for timd in timds if
        timd.get('startingLevel') == 2]))

    calculated_data['avgGoodDecisions'] = avg([
        timd.get('numGoodDecisions') for timd in timds])
    calculated_data['avgBadDecisions'] = avg([
        timd.get('numBadDecisions') for timd in timds])

    calculated_data['avgTimeIncap'] = avg([
        timd['calculatedData'].get('timeIncap') for timd in timds])
    calculated_data['avgTimeImpaired'] = avg([
        timd['calculatedData'].get('timeImpaired') for timd in timds])
    calculated_data['avgTimeClimbing'] = avg([
        timd['calculatedData'].get('timeClimbing') for timd in timds])

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

    calculated_data['lfmLemonLoadSuccess'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'lemon' and
        (action.get('zone') == 'leftLoadingStation' or
         action.get('zone') == 'leftLoadingStation')]))

    calculated_data['lfmOrangeSuccessAll'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange']))
    calculated_data['lfmOrangeSuccessDefended'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is True]))
    calculated_data['lfmOrangeSuccessUndefended'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is False]))
    calculated_data['lfmOrangeSuccessL1'] = round(100.0 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['lfmOrangeSuccessL2'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 2]))
    calculated_data['lfmOrangeSuccessL3'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 3]))

    calculated_data['lfmLemonSuccessAll'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon']))
    calculated_data['lfmLemonSuccessDefended'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is True]))
    calculated_data['lfmLemonSuccessUndefended'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is False]))
    calculated_data['lfmLemonSuccessL1'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['lfmLemonSuccessL2'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 2]))
    calculated_data['lfmLemonSuccessL3'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 3]))
    calculated_data['lfmLemonSuccessFromSide'] = round(100 * avg([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('side') != 'near']))

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

    calculated_data['sdAvgOrangesScored'] = np.std([
        timd['calculatedData'].get('orangesScored') for timd in timds])
    calculated_data['sdAvgLemonsScored'] = np.std([
        timd['calculatedData'].get('lemonsScored') for timd in timds])
    calculated_data['sdAvgOrangesFouls'] = np.std([
        timd['calculatedData'].get('orangeFouls') for timd in timds])
    calculated_data['sdAvgLemonsSpilled'] = np.std([
        timd['calculatedData'].get('lemonsSpilled') for timd in timds])

    calculated_data['sdLemonLoadSuccess'] = round(100 * np.std([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'lemon' and
        (action.get('zone') == 'leftLoadingStation' or
         action.get('zone') == 'leftLoadingStation')]))

    calculated_data['sdOrangeSuccessAll'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange']))
    calculated_data['sdOrangeSuccessDefended'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is True]))
    calculated_data['sdOrangeSuccessUndefended'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is False]))
    calculated_data['sdOrangeSuccessL1'] = round(100.0 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['sdOrangeSuccessL2'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 2]))
    calculated_data['sdOrangeSuccessL3'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 3]))

    calculated_data['sdLemonSuccessAll'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon']))
    calculated_data['sdLemonSuccessDefended'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is True]))
    calculated_data['sdLemonSuccessUndefended'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is False]))
    calculated_data['sdLemonSuccessL1'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['sdLemonSuccessL2'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 2]))
    calculated_data['sdLemonSuccessL3'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 3]))
    calculated_data['sdLemonSuccessFromSide'] = round(100 * np.std([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('side') != 'near']))

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

    calculated_data['p75AvgOrangesScored'] = p75([
        timd['calculatedData'].get('orangesScored') for timd in timds])
    calculated_data['p75AvgLemonsScored'] = p75([
        timd['calculatedData'].get('lemonsScored') for timd in timds])
    calculated_data['p75AvgOrangesFouls'] = p75([
        timd['calculatedData'].get('orangeFouls') for timd in timds])
    calculated_data['p75AvgLemonsSpilled'] = p75([
        timd['calculatedData'].get('lemonsSpilled') for timd in timds])

    calculated_data['p75LemonLoadSuccess'] = round(100 * p75([
        action['didSucceed'] for timd in lfm_timds for
        action in timd.get('timeline') if
        action.get('type') == 'intake' and
        action.get('piece') == 'lemon' and
        (action.get('zone') == 'leftLoadingStation' or
         action.get('zone') == 'leftLoadingStation')]))

    calculated_data['p75OrangeSuccessAll'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange']))
    calculated_data['p75OrangeSuccessDefended'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is True]))
    calculated_data['p75OrangeSuccessUndefended'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('wasDefended') is False]))
    calculated_data['p75OrangeSuccessL1'] = round(100.0 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['p75OrangeSuccessL2'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 2]))
    calculated_data['p75OrangeSuccessL3'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'orange' and
        action.get('level') == 3]))

    calculated_data['p75LemonSuccessAll'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeli'p75) if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon']))
    calculated_data['p75LemonSuccessDefended'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is True]))
    calculated_data['p75LemonSuccessUndefended'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('wasDefended') is False]))
    calculated_data['p75LemonSuccessL1'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') != 3 and
        action.get('level') != 2]))
    calculated_data['p75LemonSuccessL2'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 2]))
    calculated_data['p75LemonSuccessL3'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('level') == 3]))
    calculated_data['p75LemonSuccessFromSide'] = round(100 * p75([
        action['didSucceed'] for timd in timds for
        action in timd.get('timeline') if
        action.get('type') == 'placement' and
        action.get('piece') == 'lemon' and
        action.get('side') != 'near']))

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


    return calculated_data

# Uses the team number to find all the TIMDs for the passed team.
TIMDS = []
for timd in os.listdir(utils.create_file_path('data/cache/timds')):
    if TEAM_NUMBER in timd:
        with open(utils.create_file_path(
                f'data/cache/timds/{timd}')) as timd_file:
            TIMDS.append(timd_file.read())

FINAL_TEAM_DATA = team_calculations(TIMDS)

# Save data in local cache
with open(utils.create_file_path(f'data/teams/{TEAM_NUMBER}.json'),
          'w') as file:
    json.dump(FINAL_TEAM_DATA, file)

# Save data in Firebase upload queue
with open(utils.create_file_path(
        f'data/upload_queue/teams/{TEAM_NUMBER}.json'), 'w') as file:
    json.dump(FINAL_TEAM_DATA, file)
