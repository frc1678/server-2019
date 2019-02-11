# External import
import subprocess
# Internal imports
import utils

serials_dict = {
    # Green case tablets (Scouts 1-8)
    "094d5740":"Scout 1",
    "0904a28b":"Scout 2",
    "008fce263":"Scout 3",
    "005efadbb":"Scout 4",
    "0094d26f1":"Scout 5",
    "00ac0ed11":"Scout 6",
    "00a2849de":"Scout 7",
    "094d73e6":"Scout 8",
    # Black case tablets (Scouts 9-18)
    "":"Scout 9",  #TODO
    "015d256469480409":"Scout 10",
    "015d21d505281419":"Scout 11",
    "015d2568753c1408":"Scout 12",
    "015d2856d607f015":"Scout 13",
    "015d21d939641207":"Scout 14",
    "015d2856d6202206":"Scout 15",
    "015d172c98041412":"Scout 16",
    "015d188421480008":"Scout 17",
    "015d2568753c0200":"Scout 18",
    # Fire tablets without cases (Backups (1-5)
    "G000H40563460VSC":"Backup 1",
    "G000H4056383066L":"Backup 2",
    "G000H40563460T65":"Backup 3",
    "G000H404610600EK":"Backup 4",
    "":"Backup 5",  #TODO
    # this does not include serial numbs for super scouting tablets
    # (those are the ones named "red", "blue", & "purple")
}

# send file from computer to tablets and confirm that they're received
path = utils.create_file_path("data/assignments/assignments.txt", True)
# Continuously load files on to the tablet
# so that it gets loaded on whenever a tablet is plugged in.

while True:
    # stores output from "adb devices" command in var "output"
    # "adb devices" finds serials of all connected tablets (USB cable)
    output = str(subprocess.check_output("adb devices".split(" ")))
    # split output values at each "\\n" and remove last two and first words
    # of the list so it only contains needed information
    output = output.split("\\n")[1:-2]
    # Now each word in output[] is a serial followed by a "\\t" and other stuff
    # Cut off everything except the serial, which is from the beginning of the
    # line to the "\\t".
    devices = [word.split("\\t")[0] for word in output]
    # iterate through each device serial number to copy file to it
    for device in devices:
        # use dictionary to find device name
        device_name = serials_dict[device]
        # using subprocess, call 'adb push' command
        # which uses Android Debug Bridge (adb) to copy files
        subprocess.call(f"adb -s {device} push '{path}' \
                         '/mnt/sdcard/bluetooth/assignments.txt'",
                        shell=True)
        print(f"Loaded file {path} onto tablet \"{device_name}\"")
    print("\n")
