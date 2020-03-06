import copy
from typing import Dict, Union

import ROOT


def get_objects_from_file(root_file_path:str) -> dict:
  root_file = ROOT.TFile(root_file_path)
  keys=root_file.GetListOfKeys()
  object_dict = {}
  for i, item in enumerate(keys):
    current_object = item.ReadObj()
    current_object_name = current_object.GetName()
    object_dict[current_object_name] = copy.deepcopy(current_object)
  return object_dict


def has_sub_string(check_string:str, sub_strings:Union[str, list]) -> bool:
  if type(sub_strings) is list:
    for sub_string in sub_strings:
      if sub_string in check_string:
        return True
  elif type(sub_strings) is str:
    if sub_strings in check_string:
      return True
  return False


def is_supported_hist(checked_object) -> bool:
  """Checks if the object is supported histogram type."""
  is_th1d = False
  is_th1f = False
  if type(checked_object) == type(ROOT.TH1D()):
    is_th1d = True
  if type(checked_object) == type(ROOT.TH1F()):
    is_th1f = True
  if is_th1d or is_th1f:
    return True
  else:
    return False