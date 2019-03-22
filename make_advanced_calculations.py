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
    agility_weight = 0.8
    speed_weight = 0.2
    driver_ability = calculated_data['agilityZScore'] * agility_weight + \
                     calculated_data['speedZScore'] * speed_weight
    return driver_ability

def calculate_first_pick_ability(calculated_data):
    """Calculates the relative first pick score for a team.

    calculated_data is the dictionary of calculated_data calculated for
    a team."""
    # Weights for how much each aspect of the robot is considered for a
    # first pick.
    level_1_weight = 0.9
    level_2_weight = 1.1
    level_3_weight = 1.1
    sandstorm_weight = 1.0
    climbing_weight = 0.2

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
    sand_score *= sandstorm_weight

    # Scores for points scored in the endgame.
    end_game_score = max([3 * float(calculated_data['climbSuccessL1']) / 100,
                          6 * float(calculated_data['climbSuccessL2']) / 100,
                          12 * float(calculated_data['climbSuccessL3']) / 100])
    end_game_score *= climbing_weight

    # Adds all the previous scores together to get a full first pick score.
    return sand_score + level_1_teleop_score + level_2_teleop_score + level_3_teleop_score + end_game_score

def calculate_second_pick_ability(calculated_data, max_da, min_da):
    """Calculates the relative second pick score for a team.

    calculated_data is the dictionary of calculated_data calculated for
    a team.
    max_da is the maximum driver ability in the competition, this is
    used to weight driver ability.
    min_da is the minimum driver ability in the competition, this is
    used to weight driver ability."""
    # Weights for how much each aspect of the robot is considered for a
    # second pick.
    climbing_weight = .1
    oranges_weight = 1
    lemons_weight = 1
    sandstorm_weight = 1.0
    driving_weight = 10.0

    # Scores for points gained during sandstorm.
    sand_score = max([float(calculated_data['habLineSuccessL1']) * 3 / 100,
                      float(calculated_data['habLineSuccessL2']) * 6 / 100])
    sand_score += calculated_data['avgLemonsScoredSandstorm'] * 5
    sand_score += calculated_data['avgOrangesScoredSandstorm'] * 3
    sand_score *= sandstorm_weight

    # Scores for points scored on level 1.
    level_1_teleop_score = calculated_data['avgLemonsScoredTeleL1'] * 2 * lemons_weight
    level_1_teleop_score += calculated_data['avgOrangesScoredTeleL1'] * 3 * oranges_weight

    # Scores for points scored in the endgame.
    end_game_score = max([3 * float(calculated_data['climbSuccessL1']) / 100,
                          6 * float(calculated_data['climbSuccessL2']) / 100,
                          12 * float(calculated_data['climbSuccessL3']) / 100])
    end_game_score *= climbing_weight

    # If the max_da is 0.0, all the zscores are equal and there is no
    # point to weighting it.
    if max_da == 0.0:
        driver_ability = 0.0
    else:
        # Otherwise, takes the previously calculated driverAbility and
        # weights it into the pick ability. Scales all driverAbilities
        # between 0 and 'driving_weight'.
        driver_ability = driving_weight * \
            (calculated_data['driverAbility'] - min_da)/(max_da - min_da)

    return sand_score + level_1_teleop_score + end_game_score + driver_ability

def calculate_zscores(team_average_field, team_zscore_field):
    """Calculates the zscore for a team average data point across all teams.

    team_average_field is the name of the team average data field that
    the zscore is taken from.
    team_zscore_field is the name of the team zscore data field in which
    the calculated zscore is put into."""
    averages = {team: data['calculatedData'].get(team_average_field, 0.0) for
                team, data in TEAMS.items()}

    mean = numpy.mean(list(averages.values()))
    sd = numpy.std(list(averages.values()))
    for team, average in averages.items():
        if sd == 0.0:
            TEAMS[team]['calculatedData'][team_zscore_field] = 0.0
        else:
            TEAMS[team]['calculatedData'][team_zscore_field] = (average - mean) / sd

# Gathers the calculated data from all the teams.
TEAMS = {}
for team in os.listdir(utils.create_file_path('data/cache/teams')):
    with open(utils.create_file_path(f'data/cache/teams/{team}')) as file:
        team_data = json.load(file)
    # HACK: 'calculatedData' can contain 'actualSeed' without
    # containing other 'calculatedData'
    if 'avgLemonsScoredTeleL1' in team_data.get('calculatedData').keys():
        # '.split()' removes '.txt' file ending
        TEAMS[team.split('.')[0]] = team_data

SUPER_ZSCORE_DATA_FIELDS = {
    'agilityZScore': 'avgAgility',
    'speedZScore': 'avgSpeed',
}

# Calculates zscores for teams based on data fields in 'SUPER_ZSCORE_DATA_FIELDS'
for zscore_name, average_name in SUPER_ZSCORE_DATA_FIELDS.items():
    calculate_zscores(average_name, zscore_name)

# After the zscores are calculated for all the teams, other calculations
# that use zscores can be calculated, like driverAbility and
# firstPickAbility.
for team in TEAMS.keys():
    TEAMS[team]['calculatedData']['driverAbility'] = \
        calculate_driver_ability(TEAMS[team]['calculatedData'])

# Calculates the highest and lowest driverAbility for any team and uses
# it to weigh all other driverAbilities in secondPickAbility.

# TODO: Move if-statement immediately after pulling data
if TEAMS != {}:
    MAX_DA = max([team['calculatedData']['driverAbility'] for team in
                  TEAMS.keys()])
    MIN_DA = min([team['calculatedData']['driverAbility'] for team in
                  TEAMS.keys()])
    for team in TEAMS.keys():
        TEAMS[team]['calculatedData']['firstPickAbility'] = \
            calculate_first_pick_ability(TEAMS[team]['calculatedData'])
        TEAMS[team]['calculatedData']['secondPickAbility'] = \
            calculate_second_pick_ability(TEAMS[team]['calculatedData'],
                                          MAX_DA, MIN_DA)

    # Sends data to 'cache' and 'upload_queue'
    for team, data in TEAMS.items():
        with open(utils.create_file_path(f'data/cache/teams/{team}.json'), 'w') as file:
            json.dump(data, file)
        with open(utils.create_file_path(f'data/upload_queue/teams/{team}.json'), 'w') as file:
            json.dump(data, file)
