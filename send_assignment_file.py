"""Sends assignment file to scout tablets over ADB.

Verifies that the file is successfully transfered.
ADB stands for Android Debug Bridge."""
# External imports
import subprocess
import time
# Internal imports
import utils

# Serial number to human-readable device name
DEVICE_NAMES = {
    # Green case tablets (Scouts 1-8)
    '094d5740': 'Scout 1',
    '0904a28b': 'Scout 2',
    '08fce263': 'Scout 3',
    '05efadbb': 'Scout 4',
    '094d26f1': 'Scout 5',
    '0ac0ed11': 'Scout 6',
    '0a2849de': 'Scout 7',
    '094d73e6': 'Scout 8',
    # Black case tablets (Scouts 9-18)
    '015d21098450260a': 'Scout 9',
    '015d256469480409': 'Scout 10',
    '015d21d505281419': 'Scout 11',
    '015d2568753c1408': 'Scout 12',
    '015d2856d607f015': 'Scout 13',
    '015d21d939641207': 'Scout 14',
    '015d2856d6202206': 'Scout 15',
    '015d172c98041412': 'Scout 16',
    '015d188421480008': 'Scout 17',
    '015d2568753c0200': 'Scout 18',
    # Fire tablets without cases (Backups 1-5)
    'G000H40563460VSC': 'Backup 1',
    'G000H4056383066L': 'Backup 2',
    'G000H40563460T65': 'Backup 3',
    'G000H404610600EK': 'Backup 4',
    'G0K0KH02623400GT': 'Backup 5',
    # This does not include serial numbers for super scout tablets
}

ASSIGNMENT_FILE_PATH = utils.create_file_path(
    'data/assignments/assignments.txt')

# List of devices to which 'assignments.txt' has already been sent
DEVICES_WITH_FILE = []

def file_load_success(device_id):
    """ Makes sure that the file on the tablet
    is the same as assignments.txt
    by comparing tablet_data and computer_data """
    # The 'r' option for open() indicates that
    # the file will only be used for reading from
    with open(ASSIGNMENT_FILE_PATH, 'r') as file:
        computer_data = file.read()
    try:
        # The -s flag tells adb the serial number of which device to use
        tablet_data = subprocess.check_output(
            f'adb -s {device_id} shell cat /mnt/sdcard/bluetooth/assignments.txt',
            shell=True)
    except FileNotFoundError:
        return False
    # tablet_data is a "byte-like string"
    # That means when we convert it to a string, it will look like
    # b"Hello world" so we use [2:-1] to remove the b" at the
    # beginning and the " at the end
    # Also, it has \r\n everywhere there should be a newline
    # instead of an actual newline, so we replace r'\r\n' with '\n'
    tablet_data = tablet_data.decode('utf-8').replace('\r\n', '\n')
    return tablet_data == computer_data

while True:
    # Stores output from 'adb devices'
    # 'adb devices' returns the serial numbers of all devices connected
    # over ADB.
    # Example output of 'adb devices':
    # "List of devices attached\n015d2568753c1408\tdevice\n015d2856d607f015\tdevice"
    OUTPUT = subprocess.check_output('adb devices', shell=True)
    # 'OUTPUT' is a byte-like string and needs to be decoded
    OUTPUT = OUTPUT.decode('utf-8')
    # check_output returns a byte string and converting that to a string
    # makes it weird, so here's what OUTPUT looks like now:
    # "b'List of devices attached\\n015d2568753c1408\\tdevice\\n015d2856d607f015\\tdevice\\n\\n'"

    # Now split OUTPUT values at each r'\n' so that OUTPUT looks like:
    # ["b'List of devices attached", '015d2568753c1408\\tdevice',
    #  '015d2856d607f015\\tdevice', '', "'"]
    # Remove last two and first words
    # of the list so it only contains needed information. OUTPUT is:
    # ['015d2568753c1408\\tdevice', '015d2856d607f015\\tdevice']
    OUTPUT = OUTPUT.rstrip('\n').split('\n')[1:]

    # Now each word in OUTPUT[] is a serial followed by a r'\t' and other info
    # Cut off everything except the serial, which is from the beginning of the
    # line to the r'\t'.
    DEVICES = [line.split('\t')[0] for line in OUTPUT]
    # Give USB connection some time to initialize
    time.sleep(.1)  # seconds
    # Iterate through each device serial number to copy file to it
    for device in DEVICES:
        if device not in DEVICES_WITH_FILE:
            # Using subprocess, call 'adb push' command
            # which uses Android Debug Bridge (adb) to copy files
            # The -s flag tells adb which device
            # to push to using its serial number
            subprocess.call(f"adb -s {device} push '{ASSIGNMENT_FILE_PATH}' \
                             '/mnt/sdcard/bluetooth/assignments.txt'",
                            shell=True)

            if file_load_success(device):
                DEVICES_WITH_FILE.append(device)
                # Use dictionary to find human-readable
                # device name from given device serial
                # Example: DEVICE_NAMES['00a2849de'] evaluates to 'Scout 7'
                device_name = DEVICE_NAMES[device]
                print(f'Loaded assignment.txt file onto tablet {device_name}')
