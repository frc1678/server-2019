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

    x is the goal constant, or the point that the involved teams are
    trying to reach. (e.g. The amount of lemons
    that need to be scored in order to fill a rocket).
    mu is the predicted output from the involved teams. (e.g. The amount
    of lemons that a team actually scored).
    sigma is the distribution of the possible outcomes for mu.

    The returned chance is the chance that mu lies on x through the
    variance of sigma."""
    # If the distribution for mu is 0, there is no chance mu will lie on
    # x unless the value for mu is the same as x, in which the
    # probability is 100%.
    if sigma == 0.0:
        return int(x == mu)
    else:
        return 1.0 - norm.cdf(x, mu, sigma)

def calculate_predicted_alliance_score(team_numbers, pred_climb_points):
    """Calculates the predicted score for an alliance.

    team_numbers is a list of team numbers (integers) on the alliance.
    pred_climb_points is the predicted climb points for the alliance."""
    total_score = 0
    # Adds the predicted climb points for the alliance.
    total_score += pred_climb_points
    for team in team_numbers:
        total_score += TEAMS[team]['calculatedData'].get('predictedSoloPoints', 0)
    return total_score

def calculate_predicted_climb_points(team_numbers):
    """Calculates the predicted climb points for an alliance.

    team_numbers is a list of team numbers (integers) on the alliance"""
    calculated_data_by_team = {team_number: \
        TEAMS[team_number]['calculatedData'] for team_number in \
        team_numbers}
    total_points = 0
    for team_number, team_calculated_data in calculated_data_by_team.items():
        # Only one team can climb to level 3, so if a team is the most
        # successful level 3 climber, no other teams can reach level 3.
        if team_calculated_data.get('climbSuccessL3', 0) == max([
                calculated_data_by_team[team_number].get('climbSuccessL3', 0) for
                team_number in team_numbers]):
            total_points += max([3 * float(team_calculated_data.get('climbSuccessL1', 0)) / 100,
                                 6 * float(team_calculated_data.get('climbSuccessL2', 0)) / 100,
                                 12 * float(team_calculated_data.get('climbSuccessL3', 0)) / 100])
        # If the team is not the most successful at level 3, it only
        # considers the team's level 1 and 2 successes.
        else:
            total_points += max([3 * float(team_calculated_data.get('climbSuccessL1', 0)) / 100,
                                 6 * float(team_calculated_data.get('climbSuccessL2', 0)) / 100])
    return total_points

def calculate_chance_climb_rp(team_numbers):
    """Calculates the chance an alliance gets the climb RP (ranking point).

    team_numbers are the team_numbers on the alliance."""
    # Each team to their 'calculatedData' dictionary
    calculated_data_by_team = {team_number: \
        TEAMS[team_number]['calculatedData'] for team_number in \
        team_numbers}

    # Template for each team to their successes for each climb level.
    base_available_teams = {}
    for team_number, team_calculated_data in calculated_data_by_team.items():
        success_by_level = {}
        for level in ['1', '2', '3']:
            success_by_level[level] = \
                team_calculated_data.get(f'climbSuccessL{level}', 0) / 100
        base_available_teams[team_number] = success_by_level

    # The two minimum options for the climb RP are one team climbing to
    # level 3 with another on level 1, and two teams climbing to level 2
    # with another on level 1.
    # All possible combinations for the RP are at these levels or above.
    rp_combinations = [[3, 1], [2, 2, 1]]
    rp_combination_chances = []

    for rp_combination in rp_combinations:
        # 'dict(base_available_teams)' makes a copy of
        # 'base_available_teams'.
        # A copy is needed in order to remove teams without altering
        # the original data.
        available_teams = dict(base_available_teams)
        # The chances that each minimum level requirement is met.
        level_chances = []
        for min_level in rp_combination:
            # If there are no available teams left, the chance of the
            # combination is 0.
            if len(available_teams) == 0:
                rp_combination_chances.append(0)
                break
            # Team to their highest success rate out of the level(s) at
            # or above the minimum required level.
            max_successes = {}
            for team in available_teams:
                # Team's success rate by level for each level between
                # (and including) the minimum level and 3.
                level_success_rates = {level: \
                    available_teams[team][str(level)] for level in \
                    range(min_level, 3+1)}
                # Gets the max success rate out of all the levels
                max_successes[team] = max(level_success_rates.values())
            # After each team's highest success rate is taken, the
            # absolute highest success rate for the remaining teams is
            # added to the list of chances for the RP combination. Also,
            # the team is removed from the available teams because they
            # already were used for a previous minimum level.
            best_team = max(max_successes, key=max_successes.get)
            level_chances.append(max_successes[best_team])
            available_teams.pop(best_team)
        # Multiplies all the chances for the different minimum levels to
        # find the total chance for the RP combination.
        rp_combination_chance = 1
        for chance in level_chances:
            rp_combination_chance *= chance
        rp_combination_chances.append(rp_combination_chance)

    # Assumes that the alliance will go will the RP combination that has
    # the highest chance of success, so the chance for a climb RP is the
    # max of all the RP combination chances.
    return max(rp_combination_chances)

def calculate_chance_rocket_rp(team_numbers):
    """Calculates the chance an alliance gets the rocket ranking point.

    team_numbers are the team_numbers on the alliance."""
    calculated_data_by_team = [TEAMS[team]['calculatedData'] for team in
                             team_numbers]
    # Calculates the chances that the alliance places 6 lemons, then
    # multiplies it by the chance the alliance places 6 oranges.
    # [-2:] splices the list to only include the two highest lemon scorers.
    lemons_scored = sum(sorted([team_calculated_data['avgLemonsScored'] \
        for team_calculated_data in calculated_data_by_team])[-2:])
    lemon_sd = max([team_calculated_data['sdAvgLemonsScored'] for \
        team_calculated_data in calculated_data_by_team])
    lemon_chance = probability_density(6.0, lemons_scored, lemon_sd)

    oranges_scored = sum(sorted([team_calculated_data['avgOrangesScored'] \
        for team_calculated_data in calculated_data_by_team])[-2:])
    orange_sd = max([team_calculated_data['sdAvgOrangesScored'] for \
        team_calculated_data in calculated_data_by_team])
    orange_chance = probability_density(6.0, oranges_scored, orange_sd)

    return lemon_chance * orange_chance

def calculate_predicted_rps(calculated_data, color):
    """Calculates the predicted number of rps for an alliance.

    calculated_data is the prediction data for the match.
    color is the alliance color which is being calculated."""
    if color == 'red':
        win = 2 if calculated_data['redPredictedScore'] > \
            calculated_data.get('bluePredictedScore', 0) else 0
        total = win + calculated_data['redChanceClimbRP'] + \
            calculated_data['redChanceRocketRP']
        return total
    else:
        win = 2 if calculated_data['bluePredictedScore'] > \
            calculated_data.get('redPredictedScore', 0) else 0
        total = win + calculated_data['blueChanceClimbRP'] + \
            calculated_data['blueChanceRocketRP']
        return total

# Gathers the calculated data from all the teams.
TEAMS = {}
for team in os.listdir(utils.create_file_path('data/cache/teams')):
    with open(utils.create_file_path(f'data/cache/teams/{team}')) as file:
        team_data = json.load(file)
    # Checks if the team has calculated data before considering them for
    # predictions.
    if team_data.get('calculatedData') is not None:
        # '.split()' removes '.txt' file ending
        TEAMS[team.split('.')[0]] = team_data

# Gathers the matches in the competition. These matches are cached from
# the tba match schedule when the server first runs.
MATCH_SCHEDULE = {}
for match in os.listdir(utils.create_file_path('data/cache/match_schedule')):
    with open(utils.create_file_path(f'data/cache/match_schedule/{match}')) as file:
        match_data = json.load(file)
    # '.split()' removes '.txt' file ending
    MATCH_SCHEDULE[match.split('.')[0]] = match_data

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

# Each team to a list of the predicted rps they recieved in each of
# their matches.
PREDICTED_RPS_BY_TEAM = {}
for match in MATCH_SCHEDULE.keys():
    # The calculated_data dictionary where all the calculated match data
    # will be stored.
    calculated_data = {}

    # Iterates through each of the alliances to do predictions on both
    # of them.
    for alliance_color in ['red', 'blue']:
        alliance = MATCH_SCHEDULE[match][f'{alliance_color}Teams']

        alliance = [team for team in alliance if \
            TEAMS.get(team) is not None]
        if len(alliance) == 0:
            continue
        calculated_data[f'{alliance_color}PredictedClimbPoints'] = \
            calculate_predicted_climb_points(alliance)
        calculated_data[f'{alliance_color}PredictedScore'] = \
            calculate_predicted_alliance_score(alliance, \
            calculated_data[f'{alliance_color}PredictedClimbPoints'])
        calculated_data[f'{alliance_color}ChanceClimbRP'] = \
            calculate_chance_climb_rp(alliance)
        calculated_data[f'{alliance_color}ChanceRocketRP'] = \
            calculate_chance_rocket_rp(alliance)

        if MATCHES.get(match) is None:
            MATCHES[match] = {}

        # Uses actual rps instead of predicted rps when available.
        # HACK: This should be handled when calculating predicted rps instead.
        if MATCHES[match].get(f'{alliance_color}ActualRPs') is None:
            calculated_data[f'{alliance_color}PredictedRPs'] = \
                calculate_predicted_rps(calculated_data, alliance_color)
        else:
            calculated_data[f'{alliance_color}PredictedRPs'] = \
                MATCHES[match][f'{alliance_color}ActualRPs']

        for team in MATCH_SCHEDULE[match][f'{alliance_color}Teams']:
            if PREDICTED_RPS_BY_TEAM.get(team) is None:
                PREDICTED_RPS_BY_TEAM[team] = []
            PREDICTED_RPS_BY_TEAM[team].append(calculated_data[
                f'{alliance_color}PredictedRPs'])

    # Adds the prediction data to the 'calculatedData' key in the match
    # dictionary.
    if MATCHES.get(match) is None:
        MATCHES[match] = {}
    MATCHES[match]['calculatedData'] = calculated_data

# All the teams in order of their average predictedRPs from highest to lowest.
PREDICTED_RP_LIST = {team: sum(predicted_rps) / len(predicted_rps) for \
    team, predicted_rps in PREDICTED_RPS_BY_TEAM.items()}
SEED_ORDER = sorted(PREDICTED_RP_LIST.keys(), key=PREDICTED_RP_LIST.get, reverse=True)

# 'enumerate(, 1)' starts seeding at 1
for seed, team in enumerate(SEED_ORDER, 1):
    if TEAMS.get(team) is not None:
        TEAMS[team]['calculatedData']['predictedRPs'] = \
            sum(PREDICTED_RPS_BY_TEAM[team])
    TEAMS[team]['calculatedData']['predictedSeed'] = seed

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
