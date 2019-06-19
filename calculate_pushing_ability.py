#!/usr/bin/python3.6
"""Calculates pushing ability Elos.
For more info, about how Elo works, see:
https://en.wikipedia.org/wiki/Elo_rating_system"""
# External imports
import json
import os
# Internal imports
import decompressor
import utils

TEMP_SUPER_FILES = os.listdir(utils.create_file_path('data/cache/temp_super'))
# Sorts by match number, since Elo needs to be in chronological order
TEMP_SUPER_FILES.sort(key=lambda file_name: file_name.split('-')[0].split('Q')[1])

PUSHING_BATTLES = []
for temp_super_file in TEMP_SUPER_FILES:
    with open(utils.create_file_path(
            f'data/cache/temp_super/{temp_super_file}'), 'r') as file:
        compressed_temp_super = file.read()
    decompressed_pushing_battles = \
        decompressor.decompress_temp_super_pushing_battles(
            compressed_temp_super)
    PUSHING_BATTLES += decompressed_pushing_battles

# Constants:
# C is used for calculating win probability. When team A has CONSTANT_C
# more Elo than team B, team A is predicted to win 10 out of 11 battles
CONSTANT_C = 160
# K is proportional to how much a single match affects Elo ratings
CONSTANT_K = 100
CONSTANT_VALUE = {
    'largeWin': 1.0,
    # Relative worth of a small win compared to a large win
    'smallWin': 0.6,
}

# Team number to their ELO
ELOS = {}

for pushing_battle in PUSHING_BATTLES:
    # Uses 500 as the starting Elo for a team that doesn't already have one.
    winner_old_elo = ELOS.get(pushing_battle['winner'], 500)
    loser_old_elo = ELOS.get(pushing_battle['loser'], 500)

    winner_weighted_ranking = 10 ** (winner_old_elo / CONSTANT_C)
    loser_weighted_ranking = 10 ** (loser_old_elo / CONSTANT_C)

    # Expected win rate for the robot that ended up winning.
    winner_expected_win_rate = winner_weighted_ranking / (
        winner_weighted_ranking + loser_weighted_ranking)
    # If f(x) = winner_expected_win_rate
    # and x = winner_old_elo - loser_old_elo
    # then the graph of f(x) is a logistic curve.
    # f(x) = 1/(1+10**(-x/CONSTANT_C))

    if pushing_battle['winMarginIsLarge'] is True:
        win_value = CONSTANT_VALUE['largeWin']
    else:
        win_value = CONSTANT_VALUE['smallWin']

    winner_new_elo = winner_old_elo + CONSTANT_K * (win_value - \
        winner_expected_win_rate)
    loser_new_elo = loser_old_elo - CONSTANT_K * (win_value - \
        winner_expected_win_rate)

    ELOS[pushing_battle['winner']] = winner_new_elo
    ELOS[pushing_battle['loser']] = loser_new_elo

for team in ELOS.keys():
    utils.update_json_file(utils.create_file_path(
        f'data/cache/teams/{team}.json'), {'calculatedData': {'pushAbility': ELOS[team]}})
with open(utils.create_file_path('data/exports/pushing-ability-elos.json'), 'w') as file:
    json.dump(ELOS, file)
