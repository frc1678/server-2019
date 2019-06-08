#!/usr/bin/python3.6
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
    # Super scout tablets
    'HA0XCRB2': 'Red Super',
    'HA0XCUFX': 'Blue Super',
    'HA0XC9A4': 'Purple Super',
}

ASSIGNMENT_FILE_PATH = utils.create_file_path(
    'data/assignments/assignments.txt')

# List of devices to which 'assignments.txt' has already been sent
DEVICES_WITH_FILE = []

def validate_file(device_id):
    """Validates that the assignment file was successfully transfered.

    Compares the assignments.txt on the tablet to the locally stored
    assignments.txt file.

    device_id is the serial number of the device"""
    # Reads the server version of assignments.txt
    with open(ASSIGNMENT_FILE_PATH, 'r') as file:
        computer_data = file.read()
    # Reads the assignments.txt file on the tablet
    # The ADB -s flag specifies a device using its serial number
    tablet_data = subprocess.check_output(
        f'adb -s {device_id} shell cat /mnt/sdcard/bluetooth/assignments.txt',
        shell=True)
    # 'tablet_data' is a byte-like string and needs to be decoded
    tablet_data = tablet_data.decode('utf-8')
    # Replaces '\r\n' with '\n' to match the UNIX format for newlines
    tablet_data = tablet_data.replace('\r\n', '\n')

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
    # '.rstrip('\n')' removes trailing newlines
    # [1:] removes 'List of devices attached'
    OUTPUT = OUTPUT.rstrip('\n').split('\n')[1:]
    # Remove '\tdevice' from each line
    DEVICES = [line.split('\t')[0] for line in OUTPUT]

    # Wait for USB connection to initialize
    time.sleep(.1)  # .1 seconds

    for device in DEVICES:
        if device not in DEVICES_WITH_FILE:
            # Calls 'adb push' command, which uses the Android Debug
            # Bridge (ADB) to copy the assignment file to the tablet.
            # The -s flag specifies the device by its serial number.
            subprocess.call(
                f"adb -s {device} push '{ASSIGNMENT_FILE_PATH}' '/mnt/sdcard/bluetooth/assignments.txt'",
                shell=True)

            if validate_file(device) is True:
                DEVICES_WITH_FILE.append(device)
                # Convert serial number to human-readable name
                # Example: '00a2849de' becomes 'Scout 7'
                device_name = DEVICE_NAMES[device]
                print(f'Loaded assignment file onto {device_name} tablet.')
