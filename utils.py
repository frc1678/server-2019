"""Holds variables + functions that are shared across server files."""
import os

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def create_file_path(path_after_main, create_directories=False):
    """Joins the path of the directory this script is in with the path
    that is passed to this function.

    path_after_main is the path from inside the main directory.  For
    example, the path_after_main for server.py would be 'server.py'
    because it is located directly in the main directory.
    create_directories will create the directories in the path if they
    do not exist.  Assumes that all files names include a period.
    Defaults to false."""
    # Removes trailing slash in 'path_after_main' (if it exists)
    if path_after_main[-1] == '/':
        path_after_main = path_after_main[:-1]

    if create_directories is True:
        # Checks if the last item in the path is a file
        if '.' in path_after_main.split('/')[-1]:
            # Removes everyhing after the last '/' (including the '/')
            directories = '/'.join(path_after_main.split('/')[:-1])
        # The last item is a directory
        else:
            directories = path_after_main
        # 'os.makedirs' recursively creates directories (i.e.
        # 'os.makedirs' will create multiple directories, if needed)
        os.makedirs(os.path.join(MAIN_DIRECTORY, directories), exist_ok=True)
    return os.path.join(MAIN_DIRECTORY, path_after_main)
