import glob
import os


def get_file_list(directory, search_pattern, out_name_pattern="None"):
    """Gets a full list of file under given directory with given name pattern

  To use:
  >>> get_file_list("path/to/directory", "*.root")

  Args:
    directory: str, path to search files
    search_pattern: str, pattern of files to search

  Returns:
    A list of file absolute path & file name
  """
    # Get absolute path
    print("glob pattern: " + directory + "/" + search_pattern)
    absolute_file_list = glob.glob(directory + "/" + search_pattern)
    if len(absolute_file_list) == 0:
        print("empty file list, please check input(in get_file_list)")
    # Get file name match the pattern
    file_name_list = [os.path.basename(path) for path in absolute_file_list]
    # check duplicated name in file_name_list
    for name in file_name_list:
        num_same_name = 0
        for name_check in file_name_list:
            if name == name_check:
                num_same_name += 1
        if num_same_name > 1:
            print("same file name detected(in get_file_list)")
    return absolute_file_list, file_name_list
