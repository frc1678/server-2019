#!/usr/bin/python3.6
"""Calculate SPRs (Scout Precision Rankings).

Used in consolidation and to identify and address issues with scouting.
These issues are often caused by misunderstanding or actions that have
an ambiguous input.  With SPRs, these questions can be cleared up during
scout training and competition to decrease errors in the future."""
# External imports
import csv
import json
import os
# Internal imports
import decompressor
import utils

TEMP_TIMDS = os.listdir(utils.create_file_path('data/cache/temp_timds'))
TIMDS = os.listdir(utils.create_file_path('data/cache/timds'))

# Scout name to SPR breakdown dictionary
# Example format: 'Sam C': {'placement': {'correct': 3}, {'total': 10}}
SPRS = {}

def register_value(scout_name_, data_field_, is_correct):
    """Registers correct or incorrect value in 'SPRS'."""
    if SPRS.get(scout_name_) is None:
        SPRS[scout_name_] = {}
    if SPRS[scout_name_].get(data_field_) is None:
        SPRS[scout_name_][data_field_] = {}
    previous_breakdown = SPRS[scout_name_][data_field_]
    previous_correct = previous_breakdown.get('correct', 0)
    previous_total = previous_breakdown.get('total', 0)
    if is_correct is True:
        SPRS[scout_name_][data_field_]['correct'] = previous_correct + 1
    else:
        SPRS[scout_name_][data_field_]['correct'] = previous_correct
    SPRS[scout_name_][data_field_]['total'] = previous_total + 1

for temp_timd in TEMP_TIMDS:
    with open(utils.create_file_path(
            f'data/cache/temp_timds/{temp_timd}'), 'r') as file:
        file_data = file.read()
    # Removes trailing newline (if it exists) from file data.
    # Many file editors will automatically add a newline at the end of files.
    file_data = file_data.rstrip('\n')

    decompressed_temp_timd = decompressor.decompress_temp_timd(file_data)
    temp_timd_name = list(decompressed_temp_timd)[0]
    temp_timd_data = decompressed_temp_timd[temp_timd_name]

    timd_name = temp_timd_name.split('-')[0]
    try:
        with open(utils.create_file_path(
                f'data/cache/timds/{timd_name}.json'), 'r') as file:
            timd_data = json.load(file)
    except FileNotFoundError:
        timd_data = {}

    # Remove data fields that are not shared between tempTIMDs and TIMDs.
    # tempTIMD specific data fields
    scout_name = temp_timd_data.pop('scoutName')
    assignment_mode = temp_timd_data.pop('assignmentMode')
    cycle_number = temp_timd_data.pop('currentCycle', 0)
    app_version = temp_timd_data.pop('appVersion')
    assignment_file_timestamp = temp_timd_data.pop(
        'assignmentFileTimestamp')
    for data_field in ['timerStarted', 'scoutID']:
        temp_timd_data.pop(data_field, None)
    # TIMD specific data fields
    for data_field in ['calculatedData', 'superNotes']:
        timd_data.pop(data_field, None)

    # Compares tempTIMD to TIMD
    temp_timd_timeline = temp_timd_data.pop('timeline', [])
    timd_timeline = timd_data.pop('timeline', [])

    # Compares non-timed data fields
    for key, value in temp_timd_data.items():
        timd_value = timd_data.get(key)
        if value == timd_value:
            register_value(scout_name, key, True)
        else:
            register_value(scout_name, key, False)

    # Compares the number of occurrences of each action type in the timeline
    for type_ in ['intake', 'placement', 'drop', 'pinningFoul', 'climb',
                  'incap', 'unincap', 'startDefense', 'endDefense']:
        temp_timd_type_occurrences = 0
        for action in temp_timd_timeline:
            if action['type'] == type_:
                temp_timd_type_occurrences += 1
        timd_type_occurrences = 0
        for action in timd_timeline:
            if action['type'] == type_:
                timd_type_occurrences += 1
        if temp_timd_type_occurrences == timd_type_occurrences:
            register_value(scout_name, type_, True)
        else:
            register_value(scout_name, type_, False)

    # Increments 'matchesScouted'
    SPRS[scout_name]['matchesScouted'] = SPRS[scout_name].get(
        'matchesScouted', 0) + 1

# Calculates overall SPR
for scout_name, scout_breakdown in SPRS.items():
    correct = 0
    total = 0
    for data_field, breakdown in scout_breakdown.items():
        if data_field != 'matchesScouted':
            correct += breakdown['correct']
            total += breakdown['total']
    SPRS[scout_name]['overall'] = correct / total

# Saves SPRS in a json file
with open(utils.create_file_path('data/sprs/sprs.json'), 'w') as file:
    json.dump(SPRS, file)

# Exports SPRS to a CSV file
SPR_KEYS = ['scoutName', 'overall', 'matchesScouted']
with open(utils.create_file_path(f'data/sprs/sprs.csv'),
          'w') as file:
    CSV_WRITER = csv.DictWriter(file, fieldnames=SPR_KEYS)
    CSV_WRITER.writeheader()
    for scout, breakdown in SPRS.items():
        scout_breakdown = {}
        for key in SPR_KEYS:
            if key == 'scoutName':
                scout_breakdown[key] = scout
            else:
                scout_breakdown[key] = breakdown[key]
        CSV_WRITER.writerow(scout_breakdown)
