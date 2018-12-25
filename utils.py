"""Holds variables + functions that are shared across server files."""
import os

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def create_file_path(path_after_main):
    """Joins the path of the directory this script is in with the path
    that is passed to this function.

    path_after_main is the path from inside the main directory.  For
    example, the path_after_main for server.py would be 'server.py'
    because it is located directly in the main directory."""
    return os.path.join(MAIN_DIRECTORY, path_after_main)
