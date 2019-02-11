# External import
import subprocess
# Internal imports
import utils

serials_dict = {
    # Green case tablets (Scouts 1-8)
    "094d5740":"Scout 1",
    "008fce263":"Scout 3",
    "005efadbb":"Scout 4",
    "0094d26f1":"Scout 5",
    "00ac0ed11":"Scout 6",
    "00a2849de":"Scout 7",
    # Black case tablets (Scouts 9-18)
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
    "G000H404610600EK":"Backup 4"
    # this does not include serial numbs for super scouting tablets (red & blue & purple)
}

# send file from computer to tablets and confirm that they're received
path = utils.create_file_path("data/assignments/assignments.txt", True)
# Continuously load files on to the tablet
# so that it gets loaded on whenever a tablet is plugged in.

# TODO(Apurva or Nathan): figure out how to get a confirmation message
# when the file is received.
while True:
    # retrieves output from "adb devices" command to
    # find tablet serial numbers and convert them to strings
    output = str(subprocess.check_output("adb devices".split(" ")))
    # split output values at each \n and remove last two and first parts
    # of the list so it only contains needed information
    output = output.split("\\n")[1:-2]
    # cut off unnecessary part of word
    # the serial number is from the beginning of the word to the "\t"
    devices = [word.split("\\t")[0] for word in output]
    #TODO(Apurva): add dictionary that relates each serial number to a
    # scouting tablet
    for device in devices:
        device_name = serials_dict[device]
        # using subprocess, call 'adb push' command
        # which uses Android Debug Bridge (adb) to copy files
        subprocess.call(f"adb -s {device} push '{path}' '/mnt/sdcard/bluetooth/assignments.txt'",
                        shell=True)
        print(f"Loaded file {path} onto tablet \"{device_name}\"")
    print("\n")


