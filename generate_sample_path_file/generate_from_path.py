"""
Get absolute file path under given directory and save as a txt file.

Usage:
python generate_from_path.py PATH_TO_DIRECTORY SEARCH_PATTERN OUTPUT_FILE_PATH

"""

import os
import sys

from get_file_list import *

if len(sys.argv) != 4:
  print("Wrong usage! To use:")
  print("python generate_from_path.py PATH_TO_DIRECTORY 'SEARCH_PATTERN' OUTPUT_FILE_PATH")
  exit(1)

absolute_file_list, file_name_list = get_file_list(sys.argv[1], sys.argv[2])

print("*" * 80)
print("file path list example:")
example_range = 10
if example_range > len(absolute_file_list):
  example_range = len(absolute_file_list)
for i in range(example_range):
  print(os.path.abspath(absolute_file_list[i]))
print("*" * 80)

with open(sys.argv[3], 'w') as f:
  for path in absolute_file_list:
    f.write("%s\n" % os.path.abspath(path))
