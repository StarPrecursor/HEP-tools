"""
Get absolute file path with under given directory with given search pattern
prefixs in a file and save as a output txt file.

Usage:
"python generate_from_directory_list.py PATH_TO_DIRECTORY PATH_TO_PATTERN_PREFIX_FILE 'SEARCH_PATTERN' OUTPUT_FILE_PATH"

"""

import os
import sys

from get_file_list import *

if len(sys.argv) < 5:
  print("Wrong usage! To use:")
  print("python generate_from_directory_list.py PATH_TO_DIRECTORY PATH_TO_PATTERN_PREFIX_FILE 'SEARCH_PATTERN' OUTPUT_FILE_PATH (ADD_COMMENTS)")
  exit(1)

absolute_file_list = []
with open(sys.argv[2], 'r') as directory_list_file:
  directory_list = directory_list_file.readlines()
  for directory in directory_list:
    full_pattern = '/' + directory.strip() + '/' + sys.argv[3]
    temp_path_list, _= get_file_list(sys.argv[1], full_pattern.strip())
    if sys.argv[5] == '1':
      temp_path_list_comment = []
      for path in temp_path_list:
        temp_path_list_comment.append(path + '  #' + directory)
      temp_path_list = temp_path_list_comment
    absolute_file_list += temp_path_list

print("*" * 80)
print("file path list example:")
example_range = 10
if example_range > len(absolute_file_list):
  example_range = len(absolute_file_list)
for i in range(example_range):
  print(os.path.abspath(absolute_file_list[i]))
print("*" * 80)

with open(sys.argv[4], 'w') as f:
  for path in absolute_file_list:
    f.write("%s\n" % os.path.abspath(path))
