"""Holds variables + functions that are shared across server files."""
# External imports
import os
# No internal imports

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def create_file_path(path_after_main, create_directories=True):
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

def avg(lis, exception=0.0):
    """Calculates the average of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        return sum(lis) / len(lis)


def update_json_file(file_path, updated_data):
    """Updates data in a JSON file.  (Preserves old data)

    file_path is the absolute path of the file to be updated (string)
    updated_data is the data to add to the JSON file (dict)"""
    # JSON library doesn't support loading from files that don't exist,
    # so before loading data, checks if the path is an actual file.
    if os.path.isfile(file_path) is True:
        with open(file_path, 'r') as file:
            file_data = json.load(file)
    else:
        file_data = {}
    # Used for nested dictionaries (i.e. 'calculatedData')
    for key, value in updated_data.items():
        if isinstance(value, dict):
            file_data[key] = file_data.get(key, {})
            file_data[key].update(value)
        else:
            file_data[key] = value
    with open(file_path, 'w') as file:
        json.dump(file_data, file)

def no_none_get(dictionary, key, alternative):
    """Gets the value for a key in a dictionary if it exists.

    dictionary is where the value is taken from.
    key is the key that is attempted to be retrieved from the dictionary.
    alternative is what returns if the key doesn't exist."""
    if key in list(dictionary.keys()):
        if dictionary[key] is not None:
            return dictionary[key]
        else:
            return alternative
    else:
        return alternative

