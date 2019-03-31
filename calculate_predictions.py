"""Makes predictive calculations for all teams and matches in the competition.

Called by server.py"""
# External imports
import json
import os
from scipy.stats import norm
# Internal imports
import utils

def probability_density(x, mu, sigma):
    """Finds the probability density in order to make predictive chances.

    x is the point that the chance is based on (e.g. The amount of lemons
    that need to be scored in order to fill a rocket).
    mu is the tested variable (e.g. The amount of lemons that a team
    actually scored).
    sigma is the variance of mu, in our case it is a standard deviation.
    The returned chance is the chance that mu lies on x through the
    variance of sigma.
    """
    # If the variance is 0, the only two options are 100% and 0%, so
    # return either 1 or 0 based on if mu is equal to x.
    if sigma == 0.0:
        return int(x == mu)
    else:
        return 1.0 - norm.cdf(x, mu, sigma)

def calculate_predicted_alliance_score(team_numbers):
    """Calculates the predicted score for an alliance.

    team_numbers is a list of team numbers (integers) on the alliance"""
    total_score = 0
    for team in team_numbers:
        total_score += TEAMS[str(team)]['calculatedData']['predictedSoloPoints']
    return total_score

def calculate_predicted_climb_points(team_numbers):
    """Calculates the predicted climb points for an alliance.

    team_numbers is a list of team numbers (integers) on the alliance"""
    total_points = 0
    for team in team_numbers:
        team_calculated_data = TEAMS[str(team)]['calculatedData']
        # TODO: Only let one robot use climb level 3
        total_points += max([3 * float(team_calculated_data['climbSuccessL1']) / 100,
                             6 * float(team_calculated_data['climbSuccessL2']) / 100,
                             12 * float(team_calculated_data['climbSuccessL3']) / 100])
    return total_points

def calculate_chance_climb_rp(team_numbers):
    """Calculates the chance an alliance gets the climb ranking point.

    team_numbers are the team_numbers on the alliance."""
    # 'teams_calculated_data' is the list of 'calculatedData'
    # dictionaries for each team in the alliance
    teams_calculated_data = [TEAMS[str(team)]['calculatedData'] for team
                             in team_numbers]
    # The two common options for the climb rp are one team climbing to
    # level 3 with another on level 1, and two teams climbing to level 2
    # with another on level 1.
    level_3_chance = max([float(team_calculated_data['climbSuccessL3']) / 100
                          for team_calculated_data in teams_calculated_data])
    level_1_chance = max([float(team_calculated_data['climbSuccessL1']) / 100
                          for team_calculated_data in teams_calculated_data])
    level_3_rp_chance = level_3_chance * level_1_chance

    level_2_climb_chances = sorted([float(team_calculated_data['climbSuccessL2']) / 100
                                    for team_calculated_data in teams_calculated_data])[-2:]
    two_level_2_climb_chance = level_2_climb_chances[0] * level_2_climb_chances[1]
    level_2_rp_chance = two_level_2_climb_chance * level_1_chance

    return max([level_3_rp_chance, level_2_rp_chance])

def calculate_chance_rocket_rp(team_numbers):
    """Calculates the chance an alliance gets the rocket ranking point.

    team_numbers are the team_numbers on the alliance."""
    teams_calculated_data = [TEAMS[str(team)]['calculatedData'] for team in
                             team_numbers]
    # Calculates the chances that the alliance places 6 lemons, then
    # multiplies it by the chance the alliance places 6 oranges. The
    # [-2:] at the end of the sorted list splits the list to only
    # include the two highest lemon scorers.
    lemons_scored = sum(sorted([team_calculated_data['avgLemonsScored'] \
        for team_calculated_data in teams_calculated_data])[-2:])
    lemon_sd = max([team_calculated_data['sdAvgLemonsScored'] for \
        team_calculated_data in teams_calculated_data])
    lemon_chance = probability_density(6.0, lemons_scored, lemon_sd)

    oranges_scored = sum(sorted([team_calculated_data['avgOrangesScored'] \
        for team_calculated_data in teams_calculated_data])[-2:])
    orange_sd = max([team_calculated_data['sdAvgOrangesScored'] for \
        team_calculated_data in teams_calculated_data])
    orange_chance = probability_density(6.0, oranges_scored, orange_sd)

    return lemon_chance * orange_chance

def calculate_predicted_rps(calculated_data, color):
    """Calculates the predicted number of rps for an alliance.

    calculated_data is the prediction data for the match.
    color is the alliance color which is being calculated."""
    if color == 'red':
        win = 2 if calculated_data['redPredictedScore'] > \
            calculated_data['bluePredictedScore'] else 0
        total = win + calculated_data['redChanceClimbRP'] + \
            calculated_data['redChanceRocketRP']
        return total
    else:
        win = 2 if calculated_data['bluePredictedScore'] > \
            calculated_data['redPredictedScore'] else 0
        total = win + calculated_data['blueChanceClimbRP'] + \
            calculated_data['blueChanceRocketRP']
        return total

# Gathers the calculated data from all the teams.
TEAMS = {}
for team in os.listdir(utils.create_file_path('data/cache/teams')):
    with open(utils.create_file_path(f'data/cache/teams/{team}')) as file:
        team_data = json.load(file)
    # HACK: 'calculatedData' can contain 'actualSeed' without
    # containing other 'calculatedData'
    # Checks if the team has calculated data before considering them for
    # predictions.
    if 'avgLemonsScoredTeleL1' in team_data.get('calculatedData').keys():
        # '.split()' removes '.txt' file ending
        TEAMS[team.split('.')[0]] = team_data

# Gathers the matches in the competition. These matches are cached from
# the tba match schedule when the server first runs.
SCHEDULE_MATCHES = {}
for match in os.listdir(utils.create_file_path('data/cache/schedule_matches')):
    with open(utils.create_file_path(f'data/cache/schedule_matches/{match}')) as file:
        match_data = json.load(file)
    # '.split()' removes '.txt' file ending
    SCHEDULE_MATCHES[match.split('.')[0]] = match_data

# Gathers the matches that already have data in the competition. This
# data is added to, then sent to the cache and upload queue.
MATCHES = {}
for match in os.listdir(utils.create_file_path('data/cache/matches')):
    with open(utils.create_file_path(f'data/cache/matches/{match}')) as file:
        match_data = json.load(file)
    # '.split()' removes '.txt' file ending
    MATCHES[match.split('.')[0]] = match_data

for team in TEAMS.keys():
    TEAMS[team]['calculatedData']['predictedRPs'] = []

for match in SCHEDULE_MATCHES.keys():
    # The calculated_data dictionary where all the calculated match data
    # will be stored.
    calculated_data = {}

    # Iterates through each of the alliances to do predictions on both
    # of them.
    for alliance_color in ['red', 'blue']:
        alliance = SCHEDULE_MATCHES[str(match)][f'{alliance_color}Teams']

        calculated_data[f'{alliance_color}PredictedScore'] = \
            calculate_predicted_alliance_score(alliance)
        calculated_data[f'{alliance_color}PredictedClimbPoints'] = \
            calculate_predicted_climb_points(alliance)
        calculated_data[f'{alliance_color}ChanceClimbRP'] = \
            calculate_chance_climb_rp(alliance)
        calculated_data[f'{alliance_color}ChanceRocketRP'] = \
            calculate_chance_rocket_rp(alliance)

        if MATCHES[match].get(f'{alliance_color}ActualRPs') is None:
            calculated_data[f'{alliance_color}PredictedRPs'] = \
                calculate_predicted_rps(calculated_data, alliance_color)
        else:
            calculated_data[f'{alliance_color}PredictedRPs'] = \
                MATCHES[match][f'{alliance_color}ActualRPs']

    for team in SCHEDULE_MATCHES[str(match)]['redTeams']:
        if TEAMS[str(team)]['calculatedData'].get('predictedRPs') is None:
            TEAMS[str(team)]['calculatedData']['predictedRPs'] = []
        TEAMS[str(team)]['calculatedData']['predictedRPs'].append(
            calculated_data['redPredictedRPs'])
    for team in SCHEDULE_MATCHES[str(match)]['blueTeams']:
        if TEAMS[str(team)]['calculatedData'].get('predictedRPs') is None:
            TEAMS[str(team)]['calculatedData']['predictedRPs'] = []
        TEAMS[str(team)]['calculatedData']['predictedRPs'].append(
            calculated_data['bluePredictedRPs'])

    # Adds the prediction data to the 'calculatedData' key in the match
    # dictionary.
    if MATCHES.get(str(match)) is None:
        MATCHES[str(match)] = {}
    MATCHES[str(match)]['calculatedData'] = calculated_data

# All the teams in order of their average predictedRPs
PREDICTED_RP_LIST = {team: (sum(TEAMS[str(team)]['calculatedData']['predictedRPs']) / \
                     len(TEAMS[str(team)]['calculatedData']['predictedRPs'])) for team in TEAMS.keys()}
SEED_ORDER = sorted(PREDICTED_RP_LIST.keys(), key=PREDICTED_RP_LIST.get, reverse=True)

for seed, team in enumerate(SEED_ORDER, 1):
    TEAMS[str(team)]['calculatedData']['predictedRPs'] = \
        sum(TEAMS[str(team)]['calculatedData']['predictedRPs'])
    TEAMS[str(team)]['calculatedData']['predictedSeed'] = seed

# Sends data to 'cache' and 'upload_queue'
for team, data in TEAMS.items():
    with open(utils.create_file_path(f'data/cache/teams/{team}.json'), 'w') as file:
        json.dump(data, file)
    with open(utils.create_file_path(f'data/upload_queue/teams/{team}.json'), 'w') as file:
        json.dump(data, file)

# Sends data to 'cache' and 'upload_queue'
for match, data in MATCHES.items():
    with open(utils.create_file_path(f'data/cache/matches/{match}.json'), 'w') as file:
        json.dump(data, file)
    with open(utils.create_file_path(f'data/upload_queue/matches/{match}.json'), 'w') as file:
        json.dump(data, file)
