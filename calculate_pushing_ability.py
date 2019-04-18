#!/usr/bin/python3
"""Calculates pushing ability ELOs."""
# External imports
import json
import os
# Internal imports
import decompressor
import utils

TEMP_SUPER_FILES = os.listdir(utils.create_file_path('data/cache/temp_super'))
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

# Constants
CONSTANT_C = 100
CONSTANT_K = 40
CONSTANT_VALUE = {
    'largeWin': 1.0,
    # Relative worth of a small win compared to a large win
    'smallWin': 0.6,
}

# Team number to their ELO
ELOS = {}

for pushing_battle in PUSHING_BATTLES:
    winner_old_elo = ELOS.get(pushing_battle['winner'], 400)
    loser_old_elo = ELOS.get(pushing_battle['loser'], 400)

    winner_weighted_ranking = 10 ** (winner_old_elo / CONSTANT_C)
    loser_weighted_ranking = 10 ** (loser_old_elo / CONSTANT_C)

    # Expected win percentage for the robot that ended up winning.
    winner_expected_win_percentage = winner_weighted_ranking / (
        winner_weighted_ranking + loser_weighted_ranking)

    if pushing_battle['winMarginIsLarge'] is True:
        win_value = CONSTANT_VALUE['largeWin']
    else:
        win_value = CONSTANT_VALUE['smallWin']

    winner_new_elo = winner_old_elo + CONSTANT_K * (win_value - \
        winner_expected_win_percentage)
    loser_new_elo = loser_old_elo - CONSTANT_K * (win_value - \
        winner_expected_win_percentage)

    ELOS[pushing_battle['winner']] = winner_new_elo
    ELOS[pushing_battle['loser']] = loser_new_elo

with open(utils.create_file_path('data/exports/pushing-abiity-elos.json'), 'w') as file:
    json.dump(ELOS, file)
