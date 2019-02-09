import utils
import subprocess

# send file from computer to tablets and confirm that they're received
path = utils.create_file_path("data/assignments/assignments.json", True)
# Continuously load files on to the tablet
# so that it gets loaded on whenever a tablet is plugged in.
# TODO(Someone): figure out how to get a confirmation message
# when the file is received.
while (True):
    subprocess.call(f"adb push '{path}' '/home/main_storage/bluetooth'",
                    shell=True)
