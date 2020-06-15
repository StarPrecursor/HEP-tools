import copy
from typing import Dict, List, Union

import ROOT


def get_highest_bin_value(hists: Union[list, "TH1Tool"]) -> float:
    """Returns highest bin value among given hist list(s)"""
    maximum_height = 0
    if type(hists) is list:
        merged_hist = merge_hists(hists)
        maximum_height = merged_hist.GetMaximum()
    else:
        maximum_height = hists.get_hist().GetMaximum()
    return maximum_height


def get_objects_from_file(root_file_path: str) -> dict:
    """Returns dict of all objects in the root file."""
    root_file = ROOT.TFile(root_file_path)
    keys = root_file.GetListOfKeys()
    object_dict = {}
    for item in keys:
        current_object = item.ReadObj()
        current_object_name = current_object.GetName()
        object_dict[current_object_name] = copy.deepcopy(current_object)
    return object_dict


def has_sub_string(check_string: str, sub_strings: Union[str, list]) -> bool:
    """Checks whether the sub_strings in the check_string.
    
    Note:
        If sub_strings is a list and there is at least one substring in
    check_string, the function will return True.

    """
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


def merge_hists(hist_list: List["TH1Tool"]) -> ROOT.TH1:
    """Returns merged input histograms."""
    out_hist = None
    merge_list = ROOT.TList()
    for id, hist_tool in enumerate(hist_list):
        hist = hist_tool.get_hist()
        if id == 0:
            out_hist = hist.Clone()
            out_hist.Reset()
        merge_list.Add(hist)
    out_hist.Merge(merge_list)
    return out_hist
