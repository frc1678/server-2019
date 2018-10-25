"""Main server file.  Runs based on listeners + infinite while loop.

Called directly by a systemctl service that automatically runs on
startup and has automatic restart.  This script runs all the database
listeners and the while loop that checks if calculations need to be
made."""
#!/usr/bin/python3.7
import os
import time
import shutil
import signal
import subprocess
import sys
import firebase_communicator

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Uses default firebase URL
# DB stands for database
DB = firebase_communicator.configure_firebase()

def create_file_path(path_after_main):
    """Joins the path of the directory this script is in with the path
    that is passed to this function.

    path_after_main is the path from inside the main directory.  For
    example, the path_after_main for server.py would be 'server.py'
    because it is located directly in the main directory."""
    return os.path.join(MAIN_DIRECTORY, path_after_main)

def delete_temp_timd_data_folder():
    """Deletes the 'data' folder and its contents, then recreates it.

    This is to remove any outdated data, since all data is re-downloaded
    when the TEMP_TIMD_STREAM is restarted."""
    # Checks if the directory exists before trying to delete it to avoid
    # causing an error.
    if os.path.isdir(create_file_path('data')):
        shutil.rmtree(create_file_path('data'))
    os.makedirs(create_file_path('data'))

def match_num_stream_handler(snapshot):
    """Runs when 'currentMatchNumber' is updated on firebase"""
    # Validates that data was correctly received and is in its expected format
    if (snapshot['event'] == 'put' and snapshot['path'] == '/' and
            isinstance(snapshot['data'], int)):
        #TODO
        print(snapshot['data'])

def cycle_num_stream_handler(snapshot):
    """Runs when 'cycleNumber' is updated on firebase"""
    # Validates that data was correctly received and is in its expected format
    if (snapshot['event'] == 'put' and snapshot['path'] == '/'):
        cycle_number = snapshot['data']
        if cycle_number is None:
            cycle_number = 0
        subprocess.call('python3 updateAssignments.py ' +
                        str(cycle_number), shell=True)

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
            delete_temp_timd_data_folder()
            return
    elif path.count('/') == 1:
        # This is moving the path into the data so it is in the same
        # format as data at the path '/'.  This allows us to use the
        # same code to save the data in our local cache later on.
        # The '[1:]' removes the slash at the beginning of the path
        data = {path[1:] : data}
    # If there is more than 1 slash in the path, the data is multiple
    # children deep.  tempTIMDs are only one child deep and this will
    # only trigger if invalid data is sent to Firebase.
    else:
        print('Error: Invalid tempTIMD data received')
        return

    # This saves each tempTIMD in a separate text file.
    for temp_timd_name, temp_timd_value in data.items():
        # This means that this tempTIMD has been deleted from Firebase
        # and we should delete it from our local copy.
        if temp_timd_value is None:
            os.remove(create_file_path('data/' + temp_timd_name + '.txt'))
        else:
            with open(create_file_path('data/' + temp_timd_name +
                                       '.txt'), 'w') as file:
                file.write(temp_timd_value)



def create_streams(stream_names=None):
    """Creates firebase streams given a list of possible streams.

    These possible streams include: MATCH_NUM_STREAM, CYCLE_NUM_STREAM,
                                    TEMP_TIMD_STREAM,"""
    # If specific streams are not given, create all of the possible streams
    if stream_names is None:
        stream_names = ['MATCH_NUM_STREAM', 'CYCLE_NUM_STREAM',
                        'TEMP_TIMD_STREAM']
    streams = {}
    # Creates each of the streams specified and stores them in the
    # streams dict.
    for name in stream_names:
        if name == 'MATCH_NUM_STREAM':
            streams[name] = DB.child('currentMatchNumber').stream(
                match_num_stream_handler)
        elif name == 'CYCLE_NUM_STREAM':
            streams[name] = DB.child('cycleNumber').stream(
                cycle_num_stream_handler)
        elif name == 'TEMP_TIMD_STREAM':
            # Used to remove any outdated data
            delete_temp_timd_data_folder()
            streams[name] = DB.child('TempQRTeamInMatchDatas').stream(
                temp_timd_stream_handler)
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

# Detects when CTRL+C is pressed, then runs handle_ctrl_c
signal.signal(signal.SIGINT, handle_ctrl_c)

# Creates all the database streams and stores them in global dict.
STREAMS = create_streams()

while True:
    # Goes through each of the streams to check if it is still active
    for streamName, stream in STREAMS.items():
        if not stream.thread.is_alive():
            print(f"Stream '{streamName}' is dead. Restarting...")
            # This creates a new stream and then updates the 'STREAMS'
            # dict to contain the new stream. 'create_streams' returns
            # a dict, which is why '.update' is called.
            STREAMS.update(create_streams([streamName]))

    # Checks list of tempTIMDs from file to determine what calculations
    # are needed.
    #TODO: Implement tempTIMD needed calculation checking

    # Updates 'lastServerRun' on firebase with epoch time that the
    # server last ran.  Used to monitor if the server is offline by
    # checking if an excess amount of time has passed since the last run
    try:
        DB.child('lastServerRun').set(time.time())
    except OSError:
        print('Warning: No internet connection')

    time.sleep(1)
