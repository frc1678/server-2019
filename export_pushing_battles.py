#!/usr/bin/python3
"""Collects and exports all Super Scout pushing battles to a CSV file."""
# External imports
import csv
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

# Orders pushing battle keys for CSV export
CSV_HEADERS = ['matchNumber', 'winner', 'loser', 'winMarginIsLarge']

with open(utils.create_file_path('data/exports/pushing-battles.csv'), 'w') as file:
    CSV_WRITER = csv.DictWriter(file, fieldnames=CSV_HEADERS)
    CSV_WRITER.writeheader()

    for pushing_battle in PUSHING_BATTLES:
        CSV_WRITER.writerow(pushing_battle)
