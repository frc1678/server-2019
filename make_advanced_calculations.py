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
    agility_weight = 0.65
    speed_weight = 0.35
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
    sand_score = max([float(calculated_data.get('habLineSuccessL1', 0)) * 3 / 100,
                      float(calculated_data.get('habLineSuccessL2', 0)) * 6 / 100])
    sand_score += calculated_data['avgLemonsScoredSandstorm'] * 5
    sand_score += calculated_data['avgOrangesScoredSandstorm'] * 3
    sand_score *= sandstorm_weight

    # Scores for points scored in the endgame.
    end_game_score = max([3 * float(calculated_data.get('climbSuccessL1', 0)) / 100,
                          6 * float(calculated_data.get('climbSuccessL2', 0)) / 100,
                          12 * float(calculated_data.get('climbSuccessL3', 0)) / 100])
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
    climbing_weight = 0.25
    oranges_weight = 0.5
    lemons_weight = 1.0
    sandstorm_weight = 1.0
    driving_weight = 18.0
    defense_weight = 3.5

    # Scores for points gained during sandstorm.
    sand_score = max([float(calculated_data.get('habLineSuccessL1', 0)) * 3 / 100,
                      float(calculated_data.get('habLineSuccessL2', 0)) * 6 / 100])
    sand_score += calculated_data['avgLemonsScoredSandstorm'] * 5
    sand_score += calculated_data['avgOrangesScoredSandstorm'] * 3
    sand_score *= sandstorm_weight

    # Scores for points scored on level 1.
    level_1_teleop_score = calculated_data['avgLemonsScoredTeleL1'] * 2 * lemons_weight
    level_1_teleop_score += calculated_data['avgOrangesScoredTeleL1'] * 3 * oranges_weight

    # Scores for points scored in the endgame.
    end_game_score = max([3 * float(calculated_data.get('climbSuccessL1', 0)) / 100,
                          6 * float(calculated_data.get('climbSuccessL2', 0)) / 100,
                          12 * float(calculated_data.get('climbSuccessL3', 0)) / 100])
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

    # When the average rank defense is None, the defense_ability should
    # be 0, because the team didn't play defense.
    if calculated_data.get('avgRankDefense') is None:
        defense_ability = 0
    else:
        # Score for defense, based around the lowest being 1, and the
        # highest being 2 times the defense weight + 1. Example: If the
        # weight is 5, the defense ability for an avgRankDefense of 1,
        # 2, and 3 would be 1, 6, and 11 respectively.
        defense_ability = (float(calculated_data['avgRankDefense']) * \
            defense_weight) - (defense_weight - 1)
    return sand_score + level_1_teleop_score + end_game_score + driver_ability + defense_ability

def calculate_third_pick_ability(calculated_data):
    """Calculates the relative third pick score for a team.

    calculated_data is the dictionary of calculated_data calculated for
    a team."""
    # Weights for how much each aspect of the robot is considered for a
    # third pick
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
    sand_score = max([float(calculated_data.get('habLineSuccessL1', 0)) * 3 / 100,
                      float(calculated_data.get('habLineSuccessL2', 0)) * 6 / 100])
    sand_score += calculated_data['avgLemonsScoredSandstorm'] * 5
    sand_score += calculated_data['avgOrangesScoredSandstorm'] * 3
    sand_score *= sandstorm_weight

    # Scores for points scored in the endgame.
    end_game_score = max([3 * float(calculated_data.get('climbSuccessL1', 0)) / 100,
                          6 * float(calculated_data.get('climbSuccessL2', 0)) / 100,
                          12 * float(calculated_data.get('climbSuccessL3', 0)) / 100])
    end_game_score *= climbing_weight

    # A third pick robot must have a driver ability greater than 0
    # (average) and must score an average of more than 1 cargo per match.
    if (calculated_data['driverAbility'] <= 0) or \
        (calculated_data['avgOrangesScored'] <= 1):
        return 0

    # Adds all the previous scores together to get a full third pick score.
    return sand_score + level_1_teleop_score + level_2_teleop_score + level_3_teleop_score + end_game_score

def calculate_zscores(team_average_field, team_zscore_field):
    """Calculates the zscore for a team average data point across all teams.

    team_average_field is the name of the team average data field that
    the zscore is taken from.
    team_zscore_field is the name of the team zscore data field in which
    the calculated zscore is put into."""
    averages = {team: data['calculatedData'][team_average_field] for
                team, data in TEAMS.items()}

    mean = numpy.mean(list(averages.values()))
    sd = numpy.std(list(averages.values()))
    for team, average in averages.items():
        TEAMS[team]['calculatedData'][team_zscore_field] = (average - mean) / sd

# Gathers the calculated data from all the teams.
TEAMS = {}
for team in os.listdir(utils.create_file_path('data/cache/teams')):
    with open(utils.create_file_path(f'data/cache/teams/{team}')) as file:
        team_data = json.load(file)
    if team_data.get('calculatedData') is not None:
        # '.split()' removes '.json' file ending
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

# TODO: Move if-statement immediately after pulling data
if TEAMS != {}:
    # Calculates the highest and lowest driverAbility for any team and uses
    # it to weigh all other driverAbilities in secondPickAbility.
    MAX_DA = max([team_data['calculatedData']['driverAbility'] for team_data
                  in TEAMS.values()])
    MIN_DA = min([team_data['calculatedData']['driverAbility'] for team_data
                  in TEAMS.values()])
    for team in TEAMS.keys():
        if TEAMS[team].get('calculatedData') is not None:
            TEAMS[team]['calculatedData']['firstPickAbility'] = \
                calculate_first_pick_ability(TEAMS[team]['calculatedData'])
            TEAMS[team]['calculatedData']['secondPickAbility'] = \
                calculate_second_pick_ability(TEAMS[team]['calculatedData'],
                                              MAX_DA, MIN_DA)
            TEAMS[team]['calculatedData']['thirdPickAbility'] = \
                calculate_third_pick_ability(TEAMS[team]['calculatedData'])

    # Gathers the matches in the competition. These matches are cached from
    # TBA when the server first runs.
    MATCH_SCHEDULE = {}
    for match_file in os.listdir(utils.create_file_path('data/cache/match_schedule')):
        with open(utils.create_file_path(f'data/cache/match_schedule/{match_file}')) as file:
            match_data = json.load(file)
        # '.split()' removes '.txt' file ending
        MATCH_SCHEDULE[match_file.split('.')[0]] = match_data

    TIMD_FILES = os.listdir(utils.create_file_path('data/cache/timds'))
    # Removes '.json' file ending.
    TIMDS = [timd_file.split('.')[0] for timd_file in TIMD_FILES]
    for team in TEAMS:
        # Matches a team has played
        matches = [timd.split('Q')[1] for timd in TIMDS if timd.split('Q')[0] == team]
        # Gets the alliance partners of a team across their matches
        alliance_members = []
        for match in matches:
            # Uses 'list()' to not associate the match schedule when
            # alliance is deleted from.
            red_alliance = list(MATCH_SCHEDULE[match]['redTeams'])
            blue_alliance = list(MATCH_SCHEDULE[match]['blueTeams'])
            if str(team) in red_alliance:
                # Sets alliance the alliance equal to those teams
                alliance = red_alliance
            # Checks if the team is in the blue alliance
            elif str(team) in blue_alliance:
                # Sets alliance the alliance equal to those teams
                alliance = blue_alliance
            else:
                print('Error: Team not in match schedule.')
            # Removes own team and leaves only alliance partners in the list
            alliance.remove(str(team))
            alliance_members += alliance

        # Scaled driver ability of the team's alliance partners
        scaled_driver_abilities = []
        for team in alliance_members:
            driver_ability = \
                TEAMS[team]['calculatedData']['driverAbility']
            # Scales driver ability so that the lowest driver ability is
            # counted as 0, and the highest is counted as 1. All other
            # values in between are scaled linearly.
            scaled_driver_ability = 1 * \
                (driver_ability - MIN_DA)/(MAX_DA - MIN_DA)
            scaled_driver_abilities.append(scaled_driver_ability)
        # Multiplies the average scaled alliance partner's driver ability
        # by the team's nonscaled driver ability to get the team's normalized
        # driver ability.
        normalized_driver_ability = utils.avg(scaled_driver_abilities) * \
            TEAMS[team]['calculatedData']['driverAbility']
        # Scales driver ability so that the lowest driver ability is
        # counted as 0, and the highest is counted as 1. All other
        # values in between are scaled linearly.
        scaled_driver_ability = 1 * \
            (driver_ability - MIN_DA)/(MAX_DA - MIN_DA)
        scaled_driver_abilities.append(scaled_driver_ability)
    # Multiplies the average scaled alliance partner's driver ability
    # by the team's nonscaled driver ability to get the team's normalized
    # driver ability.
    normalized_driver_ability = utils.avg(scaled_driver_abilities) * \
        TEAMS[team]['calculatedData']['driverAbility']
    TEAMS[team]['calculatedData']['normalizedDriverAbility'] = \
        normalized_driver_ability

# Sends data to 'cache' and 'upload_queue'
for team, data in TEAMS.items():
    with open(utils.create_file_path(f'data/cache/teams/{team}.json'), 'w') as file:
        json.dump(data, file)
    with open(utils.create_file_path(f'data/upload_queue/teams/{team}.json'), 'w') as file:
        json.dump(data, file)
