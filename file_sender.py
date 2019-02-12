""" Send file from computer to devices and confirm that they're received
Continuously load files on to the device
so that it gets loaded on whenever a device is plugged in. """
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
#TODO Test this program on EVERY SINGLE TABLET to make sure it works
# External imports
import subprocess
import time
# Internal imports
import utils

# serial number to human-readable name of device
serials_dict = {
    # Green case tablets (Scouts 1-8)
    '094d5740': 'Scout 1',
    '0904a28b': 'Scout 2',
    '008fce263': 'Scout 3',
    '005efadbb': 'Scout 4',
    '0094d26f1': 'Scout 5',
    '00ac0ed11': 'Scout 6',
    '00a2849de': 'Scout 7',
    '094d73e6': 'Scout 8',
    # Black case tablets (Scouts 9-18)
    '':'Scout 9',  #TODO(Apurva): figure out serial number for this tablet
    '015d256469480409': 'Scout 10',
    '015d21d505281419': 'Scout 11',
    '015d2568753c1408': 'Scout 12',
    '015d2856d607f015': 'Scout 13',
    '015d21d939641207': 'Scout 14',
    '015d2856d6202206': 'Scout 15',
    '015d172c98041412': 'Scout 16',
    '015d188421480008': 'Scout 17',
    '015d2568753c0200': 'Scout 18',
    # Fire tablets without cases (Backups (1-5)
    'G000H40563460VSC': 'Backup 1',
    'G000H4056383066L': 'Backup 2',
    'G000H40563460T65': 'Backup 3',
    'G000H404610600EK': 'Backup 4',
    'G0K0KH02623400GT': 'Backup 5'
    # this does not include serial numbs for super scouting tablets
    # (those are the ones named 'red', 'blue', & 'purple')
}

assignment_file_path = utils.create_file_path('data/assignments/assignments.txt', True)

# list of devices with the file so we do not copy the file
# onto the device again
devices_with_file = []

while True:
    # stores output from 'adb devices' command in var 'output'
    # 'adb devices' finds serials of all connected devices (USB cable)

    # Here's and example output of 'adb devices':
    # List of devices attached
    # 015d2568753c1408	device
    # 015d2856d607f015	device
    output = str(subprocess.check_output('adb devices'.split(' ')))
    # check_output returns a byte string and converting that to a string
    # makes it weird, so here's what output looks like now:
    # "b'List of devices attached\\n015d2568753c1408\\tdevice\\n015d2856d607f015\\tdevice\\n\\n'"

    # now split output values at each '\\n' so that output looks like:
    # ["b'List of devices attached", '015d2568753c1408\\tdevice', '015d2856d607f015\\tdevice', '', "'"]
    # remove last two and first words
    # of the list so it only contains needed information. output is:
    # ['015d2568753c1408\\tdevice', '015d2856d607f015\\tdevice']
    output = output.split('\\n')[1:-2]

    # Now each word in output[] is a serial followed by a '\\t' and other stuff
    # Cut off everything except the serial, which is from the beginning of the
    # line to the '\\t'.
    devices = [line.split('\\t')[0] for line in output]
    # iterate through each device serial number to copy file to it
    # give connection some time to initialize
    time.sleep(.1)  # seconds
    for device in devices:
        if device not in devices_with_file:
            # use dictionary to find human-readable device name given device serial
            # example: serials_dict['00a2849de'] evaluates to 'Scout 7'
            device_name = serials_dict[device]
            # using subprocess, call 'adb push' command
            # which uses Android Debug Bridge (adb) to copy files
            # the -s flag tells adb which device to push to using its serial number
            subprocess.call(f"adb -s {device} push '{assignment_file_path}' \
                             '/mnt/sdcard/bluetooth/assignments.txt'",
                            shell=True)
            devices_with_file.append(device)
            print(f'Loaded assignment.txt file onto tablet \'{device_name}\'')
