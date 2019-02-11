import utils
import subprocess

# send file from computer to tablets and confirm that they're received
path = utils.create_file_path("data/assignments/assignments.json", True)
# Continuously load files on to the tablet
# so that it gets loaded on whenever a tablet is plugged in.
#TODO(Someone): figure out how to get a confirmation message
# when the file is received.
while (True):
    output = str(subprocess.check_output("adb devices".split(" ")))
    output = output.split("\\n")[1:-2]
    # serial is a 16 character string
    devices = list(map(lambda word : word[:16],
                       output))
    #TODO(Nathan) figure out hot to get list of serial numbers
    # ("devices") from command output ("output")
    for device in devices:
        subprocess.call(f"adb -s {device} push '{path}' '/mnt/sdcard/bluetooth'",
                        shell=True)
        print(f"Loaded file \"{path}\" onto tablet with serial {device}")
    print("\n")
