"""Performs advanced team calcs on every team in the competition.

Called by server.py after team specific calculations."""
# External Imports
import os
import json
import numpy
# Internal Imports
import utils

def calculate_driver_ability(calculated_data):
    """Calculates the relative driver ability for a team using driver zscores.

    calculated_data is the calculated data for the team being calculated."""
    agile_weight = 0.8
    speed_weight = 0.2
    return (calculated_data['agilityZScore'] * agile_weight) + \
           (calculated_data['speedZScore'] * speed_weight)

def first_pick_ability(calculated_data):
    """Calculates the relative first pick score for a team.

    calculated_data is the dictionary of calculated_data calculated for
    a team."""
    # Constants that determine how much each score is weighted in
    # determining first pick ability.
    level_1_weight = 0.9  # How much we care about teams scoring on lvl 1
    level_2_weight = 1.1  # How much we care about teams scoring on lvl 2
    level_3_weight = 1.1  # How much we care about teams scoring on lvl 3
    climbing_weight = 0.2  # How much we want alliance partners to solo climb

    # Scores for points scored on level 1, 2, and 3.
    level_1_teleop_score = (2 * calculated_data['avgLemonsScoredTeleL1']
        + 3 * calculated_data['avgOrangesScoredTeleL1']) * level_1_weight
    level_2_teleop_score = (2 * calculated_data['avgLemonsScoredTeleL2']
        + 3 * calculated_data['avgOrangesScoredTeleL2']) * level_2_weight
    level_3_teleop_score = (2 * calculated_data['avgLemonsScoredTeleL3']
        + 3 * calculated_data['avgOrangesScoredTeleL3']) * level_3_weight

    # Scores for points gained during sandstorm.
    sand_score = max([float(calculated_data['habLineSuccessL1']) * 3 / 100,
                      float(calculated_data['habLineSuccessL2']) * 6 / 100])
    sand_score += calculated_data['avgLemonsScoredSandstorm'] * 5
    sand_score += calculated_data['avgOrangesScoredSandstorm'] * 3

    # Scores for points scored in the endgame.
    end_game_score = max([3 * float(calculated_data['climbSuccessL1']) / 100,
                          6 * float(calculated_data['climbSuccessL2']) / 100,
                          12 * float(calculated_data['climbSuccessL3']) / 100])
    end_game_score *= climbing_weight

    # Adds all the previous scores together to get a full first pick score.
    return sand_score + end_game_score + level_1_teleop_score + level_2_teleop_score + level_3_teleop_score

def second_pick_ability(calculated_data):
    """Calculates the relative second pick score for a team.

    calculated_data is the dictionary of calculated_data calculated for
    a team."""
    climbing_weight = .1  # How much we want alliance partners to solo climb
    #driving_weight = 10  # How much we care about driver ability
    oranges_weight = 1  # How much we want second picks to be scoring oranges
    lemons_weight = 1  # How much we want second picks to be scoring lemons

    # Scores for points gained during sandstorm.
    sand_score = max([float(calculated_data['habLineSuccessL1']) * 3 / 100,
                      float(calculated_data['habLineSuccessL2']) * 6 / 100])
    sand_score += calculated_data['avgLemonsScoredSandstorm'] * 5
    sand_score += calculated_data['avgOrangesScoredSandstorm'] * 3

    # Scores for points scored on level 1.
    level_1_teleop_score = calculated_data['avgLemonsScoredTeleL1'] * 2 * lemons_weight
    level_1_teleop_score += calculated_data['avgOrangesScoredTeleL1'] * 3 * oranges_weight

    # Scores for points scored in the endgame.
    end_game_score = max([3 * float(calculated_data['climbSuccessL1']) / 100,
                          6 * float(calculated_data['climbSuccessL2']) / 100,
                          12 * float(calculated_data['climbSuccessL3']) / 100])
    end_game_score *= climbing_weight

    # Takes the previously calculated driverAbility and weights it into
    # the pick ability.
    #driver_ability = calculated_data['driverAbility'] * driving_weight

    return sand_score + level_1_teleop_score + end_game_score #+ driver_ability

# Gathers the calculated data from all the teams.
TEAMS = {}
for team in os.listdir(utils.create_file_path('data/cache/teams')):
    with open(utils.create_file_path(f'data/cache/teams/{team}')) as team_file:
        team_data = json.load(team_file)
        if team_data.get('calculatedData') is not None:
            TEAMS[team.split('.')[0]] = team_data

# A dictionary of team to their average agility, used to generate zscores.
AGILITIES = {team : data['calculatedData']['avgAgility'] for team, data
             in TEAMS.items()}

AG_MEAN = numpy.mean(list(AGILITIES.values()))
AG_SD = numpy.std(list(AGILITIES.values()))
for team, average in AGILITIES.items():
    TEAMS[team]['calculatedData']['agilityZScore'] = (average - AG_MEAN) / AG_SD

# A dictionary of team to their average speed, used to generate zscores.
SPEEDS = {team : data['calculatedData']['avgSpeed'] for team, data in
          TEAMS.items()}

SP_MEAN = numpy.mean(list(SPEEDS.values()))
SP_SD = numpy.std(list(SPEEDS.values()))
for team, average in SPEEDS.items():
    TEAMS[team]['calculatedData']['speedZScore'] = (average - SP_MEAN) / SP_SD

# After the zscores are calculated for all the teams, other calculations
# that use zscores can be calculated, like driverAbility and
# firstPickAbility.
for team in list(TEAMS.keys()):
    TEAMS[team]['calculatedData']['driverAbility'] = \
        calculate_driver_ability(TEAMS[team]['calculatedData'])
    TEAMS[team]['calculatedData']['firstPickAbility'] = \
        first_pick_ability(TEAMS[team]['calculatedData'])
    TEAMS[team]['calculatedData']['secondPickAbility'] = \
        second_pick_ability(TEAMS[team]['calculatedData'])

# After all the teams have been calculated, they can be put back in the cache.
for team, data in TEAMS.items():
    with open(utils.create_file_path(f'data/cache/teams/{team}.json'), 'w') as team_file:
        json.dump(data, team_file)
