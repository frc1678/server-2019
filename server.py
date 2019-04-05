#!/usr/bin/python3.6
"""Main server file.  Runs based on listeners + infinite while loop.

Called directly by a systemctl service that automatically runs on
startup and has automatic restart.  This script runs all the database
listeners and the while loop that checks if calculations need to be
made."""
# External imports
import json
import os
import shutil
import signal
import subprocess
import sys
import time
# Internal imports
import firebase_communicator
import tba_communicator
import utils

# Uses default firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

def delete_cache_data_folder(folder_name):
    """Deletes a cache folder and its contents, then recreates it.

    This is to remove any outdated data, since all data is re-downloaded
    when a Firebase stream is restarted."""
    # Checks if the directory exists before trying to delete it to avoid
    # causing an error.
    if os.path.isdir(utils.create_file_path(f'data/cache/{folder_name}',
                                            False)):
        shutil.rmtree(utils.create_file_path(f'data/cache/{folder_name}',
                                             False))

def register_modified_temp_timd(temp_timd_name):
    """Removes a modified tempTIMD from LATEST_CALCULATIONS_BY_TIMD.

    This is called when a tempTIMD is removed or edited.  This function
    will cause the relevant data to be recalculated to reflect the new
    data."""
    timd_name = temp_timd_name.split('-')[0]
    if LATEST_CALCULATIONS_BY_TIMD.get(timd_name) is not None:
        LATEST_CALCULATIONS_BY_TIMD[timd_name] = (
            LATEST_CALCULATIONS_BY_TIMD[timd_name].remove(
                temp_timd_name))
        # TODO: If there is only one tempTIMD in the list, and it is
        # removed, the TIMD data will not be recalculated or deleted.
        # Need to delete TIMD data + recalculate team + match data if
        # this happens.


def match_num_stream_handler(snapshot):
    """Runs when 'currentMatchNumber' is updated on firebase"""
    # Validates that data was correctly received and is in its expected format
    if (snapshot['event'] == 'put' and snapshot['path'] == '/' and
            isinstance(snapshot['data'], int)):
        # Forwards TBA data to Teams, TIMDs, and Matches.
        subprocess.call('python3 forward_tba_data.py', shell=True)
        # Calculates SPRs (Scout Precision Rankings)
        subprocess.call('python3 calculate_sprs.py', shell=True)
        print('Did SPRs calculations')

def cycle_num_stream_handler(snapshot):
    """Runs when 'cycleNumber' is updated on firebase"""
    # Validates that data was correctly received and is in its expected format
    if (snapshot['event'] == 'put' and snapshot['path'] == '/'):
        cycle_number = snapshot['data']
        if cycle_number is None:
            cycle_number = 0
        subprocess.call(f'python3 update_assignments.py {cycle_number}',
                        shell=True)

def temp_timd_stream_handler(snapshot):
    """Runs when any new tempTIMDs are uploaded"""
    data = snapshot['data']
    path = snapshot['path']

    # This occurs when the entirety of tempTIMDs are updated
    # (stream initialization, all tempTIMDs deleted, or first tempTIMD created)
    if path == '/':
        # This means that all tempTIMDs have been wiped and we should
        # wipe our local copy.
        if data is None:
            delete_cache_data_folder('temp_timds')
            return
    elif path.count('/') == 1:
        # This is moving the path into the data so it is in the same
        # format as data at the path '/'.  This allows us to use the
        # same code to save the data in our local cache later on.
        # The '[1:]' removes the slash at the beginning of the path
        data = {path[1:]: data}
    # If there is more than 1 slash in the path, the data is multiple
    # children deep.  tempTIMDs are only one child deep and this will
    # only trigger if invalid data is sent to Firebase.
    else:
        print('Error: Invalid tempTIMD data received')
        return

    # This saves each tempTIMD in a separate text file.
    for temp_timd_name, temp_timd_value in data.items():
        # HACK: Remove trailing '\n' (newlines) in compressed tempTIMD
        # data.  This is a bug in the Scout app.
        temp_timd_value = temp_timd_value.rstrip('\n')
        # This means that this tempTIMD has been deleted from Firebase
        # and we should delete it from our local copy.
        if temp_timd_value is None:
            os.remove(utils.create_file_path(
                f'data/cache/temp_timds/{temp_timd_name}.txt'))
            # Causes the corresponding TIMD to be recalculated
            register_modified_temp_timd(temp_timd_name)
        else:
            with open(utils.create_file_path(
                    f'data/cache/temp_timds/{temp_timd_name}.txt'),
                      'w') as file:
                file.write(temp_timd_value)
            timd_name = temp_timd_name.split('-')[0]
            # This means an already existing tempTIMD has been modified
            # and needs to be recalculated.
            if temp_timd_name in LATEST_CALCULATIONS_BY_TIMD.get(
                    timd_name, []):
                register_modified_temp_timd(temp_timd_name)

def temp_super_stream_handler(snapshot):
    """Runs when any new tempSuper datas are uploaded"""
    data = snapshot['data']
    path = snapshot['path']

    # This occurs when the entirety of tempSuper datas are updated
    # (stream initialization, all tempSuper data deleted, or first
    # tempSuper created)
    if path == '/':
        # This means that all tempSuper datas have been wiped and we
        # should wipe our local copy.
        if data is None:
            delete_cache_data_folder('temp_super')
            return
    elif path.count('/') == 1:
        # This is moving the path into the data so it is in the same
        # format as data at the path '/'.  This allows us to use the
        # same code to save the data in our local cache later on.
        # The '[1:]' removes the slash at the beginning of the path
        data = {path[1:]: data}
    # If there is more than 1 slash in the path, the data is multiple
    # children deep.  tempSupers are only one child deep and this will
    # only trigger if invalid data is sent to Firebase.
    else:
        print('Error: Invalid tempSuper data received')
        return

    # This saves each tempSuper data in a separate text file.
    for temp_super_name, temp_super_value in data.items():
        # This means that this tempSuper has been deleted from Firebase
        # and we should delete it from our local copy.
        if temp_super_value is None:
            os.remove(utils.create_file_path(
                f'data/cache/temp_super/{temp_super_name}.txt'))
        else:
            with open(utils.create_file_path(
                    f'data/cache/temp_super/{temp_super_name}.txt'),
                      'w') as file:
                file.write(temp_super_value)


def create_streams(stream_names=None):
    """Creates firebase streams given a list of possible streams.

    These possible streams include: MATCH_NUM_STREAM, CYCLE_NUM_STREAM,
                                    TEMP_TIMD_STREAM, TEMP_SUPER_STREAM"""
    # If specific streams are not given, create all of the possible streams
    if stream_names is None:
        stream_names = ['MATCH_NUM_STREAM', 'CYCLE_NUM_STREAM',
                        'TEMP_TIMD_STREAM', 'TEMP_SUPER_STREAM']
    streams = {}
    # Creates each of the streams specified and stores them in the
    # streams dict.
    for name in stream_names:
        if name == 'MATCH_NUM_STREAM':
            streams[name] = DB.child(
                'scoutManagement/currentMatchNumber').stream(
                    match_num_stream_handler)
        elif name == 'CYCLE_NUM_STREAM':
            streams[name] = DB.child('scoutManagement/cycleNumber'
                                    ).stream(cycle_num_stream_handler)
        elif name == 'TEMP_TIMD_STREAM':
            # Used to remove any outdated data
            delete_cache_data_folder('temp_timds')
            streams[name] = DB.child('tempTIMDs').stream(
                temp_timd_stream_handler)
        elif name == 'TEMP_SUPER_STREAM':
            # Used to remove any outdated data
            delete_cache_data_folder('temp_super')
            streams[name] = DB.child('tempSuper').stream(
                temp_super_stream_handler)
    return streams

# signal.signal passes two arguments to this function, neither are used
def handle_ctrl_c(*args):
    """Kills this script when CTRL+C is pressed.

    Running streams to firebase prevents normal CTRL+C from exiting the
    script. In order to exit, we must first close the streams."""
    print('\n\nCTRL+C pressed. Cleaning up...')

    # Underscore used for the sole purpose of avoiding conflict with
    # global variable 'stream'. (Located in while loop)
    for stream_ in STREAMS.values():
        # If the stream is dead, we cannot close it.  If we try to close
        # a dead stream, it will stall the program.
        if stream_.thread.is_alive():
            stream_.close()
    print('All streams closed.')
    sys.exit(0)

def cache_match_schedule():
    """Requests the match schedule from TBA and adds it to the cache."""
    # HACK: Only pulls the match schedule once since the caching built
    # into tba_communicator.py is not complete.
    matches = tba_communicator.request_matches()
    for match_data in matches:
        # 'qm' stands for qualification match
        if match_data['comp_level'] == 'qm':
            red_teams = match_data['alliances']['red']['team_keys']
            blue_teams = match_data['alliances']['blue']['team_keys']
            match_number = match_data['match_number']
            # Remove 'frc' from team number and convert to integer
            # (e.g. 'frc1678' -> 1678)
            red_teams = [team[3:] for team in red_teams]
            blue_teams = [team[3:] for team in blue_teams]
            final_match_data = {
                'matchNumber': match_number,
                'redTeams': red_teams,
                'blueTeams': blue_teams,
            }
        with open(utils.create_file_path(
                f'data/cache/match_schedule/{str(match_number)}.json'), 'w') as file:
            json.dump(final_match_data, file)

# Deletes the entire 'cache' directory to remove any old data.
# Checks if the directory exists before trying to delete it to avoid
# causing an error.
if os.path.isdir(utils.create_file_path('data/cache', False)):
    shutil.rmtree(utils.create_file_path('data/cache', False))

# Detects when CTRL+C is pressed, then runs handle_ctrl_c
signal.signal(signal.SIGINT, handle_ctrl_c)

# Creates all the database streams and stores them in global dict.
STREAMS = create_streams()

# In order to make match calculations, the match schedule must be taken
# from TBA and put into the cache.
cache_match_schedule()

# Stores the tempTIMDs that have already been calculated in order to
# prevent them from being recalculated if the data has not changed.
LATEST_CALCULATIONS_BY_TIMD = {}

while True:
    # Goes through each of the streams to check if it is still active
    for stream_name, stream in STREAMS.items():
        if not stream.thread.is_alive():
            print(f"Stream '{stream_name}' is dead. Restarting...")
            # This creates a new stream and then updates the 'STREAMS'
            # dict to contain the new stream. 'create_streams' returns
            # a dict, which is why '.update' is called.
            STREAMS.update(create_streams([stream_name]))

    # Checks list of tempTIMDs from files to determine what calculations
    # are needed.

    # List of files (tempTIMDs) in the 'temp_timds' cache directory.
    TEMP_TIMD_FILES = os.listdir(utils.create_file_path(
        'data/cache/temp_timds'))
    # Stores groups of matching tempTIMDs under a single key (which is
    # the corresponding TIMD).  Used to consolidate tempTIMDs.
    # (Matching tempTIMDs are tempTIMDs for the same TIMD)
    FILES_BY_TIMD = {}
    for temp_timd in TEMP_TIMD_FILES:
        # Removes '.txt' ending.
        TEMP_TIMD_NAME = temp_timd.split('.')[0]
        # Removes scout ID to find the corresponding TIMD for the
        # tempTIMD.
        TIMD_NAME = TEMP_TIMD_NAME.split('-')[0]
        FILES_BY_TIMD[TIMD_NAME] = FILES_BY_TIMD.get(TIMD_NAME, []) + [
            TEMP_TIMD_NAME]

    # Runs calculations for each TIMD that has new data since the last
    # time it ran.
    # The calculation of TIMDs causes the corresponding match and team
    # data to be recalculated. #TODO: Update this comment w/future development
    for timd in FILES_BY_TIMD:
        if LATEST_CALCULATIONS_BY_TIMD.get(timd) != FILES_BY_TIMD[timd]:
            subprocess.call(f'python3 calculate_timd.py {timd}', shell=True)
            print(f"Did calculations for {timd}")
            LATEST_CALCULATIONS_BY_TIMD[timd] = FILES_BY_TIMD[timd]

    # Forwards tempSuper data to Matches and TIMDs.
    subprocess.call('python3 forward_temp_super.py', shell=True)

    # Makes predictions about match results.
    subprocess.call('python3 calculate_predictions.py', shell=True)

    # Runs advanced calculations for every team in the competition.
    subprocess.call('python3 make_advanced_calculations.py', shell=True)

    # Uploads data in data queue.
    subprocess.call('python3 upload_data.py', shell=True)

    # Updates 'lastServerRun' on firebase with epoch time that the
    # server last ran.  Used to monitor if the server is offline by
    # checking if an excess amount of time has passed since the last run
    try:
        DB.child('lastServerRun').set(time.time())
    except OSError:
        print('Warning: No internet connection')

    time.sleep(5)
