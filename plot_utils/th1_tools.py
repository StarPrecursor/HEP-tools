import copy
import json
import math
import os
from typing import Dict, List, Union

import ROOT

Cfg_Dict = Dict[str, Union[int, float, str, Dict[str, Union[int, float, str]]]]


class HistCollection(object):
    """Collection of histograms."""
    def __init__(self,
                 hist_list: List[ROOT.TH1],
                 collection_name: str = 'hist collection',
                 collection_title: str = 'hist collection',
                 create_new_canvas: bool = False,
                 canvas: Union[ROOT.TCanvas, None] = None) -> None:
        self.canvas = canvas
        self.collection_name = collection_name
        self.collection_title = collection_title
        self._hist_list = []
        for hist in hist_list:
            self._hist_list.append(copy.deepcopy(hist))
        if type(hist_list) is not list:
            ValueError("Invalid hist_list type.")
        if len(hist_list) < 1:
            ValueError("Empty hist_list.")
        if create_new_canvas or (canvas is None):
            self.create_canvas()

    def create_canvas(self) -> None:
        self.canvas = ROOT.TCanvas(self.collection_name + "_col",
                                   self.collection_title + "_col", 1600, 1000)

    def draw(self,
             config_str: str = "",
             legend_title: str = "legend title",
             legend_paras: list = [0.75, 0.75, 0.9, 0.9],
             draw_norm: bool = False,
             remove_empty_ends: bool = False,
             norm_factor: float = 1.) -> None:
        self.canvas.cd()
        maximum_height = -1e10
        x_min_use = math.inf
        x_max_use = -math.inf
        for hist in self._hist_list:
            # set stats 0
            hist.get_hist().SetStats(0)
            #
            if draw_norm:
                hist.update_config('y_axis', 'SetTitle', "")
                total_weight = hist.get_hist().Integral("width")
                if total_weight != 0:
                    hist.get_hist().Scale(1 / total_weight)
            # find non-zero-bin range along x axis
            x_min = hist.get_hist().FindFirstBinAbove(0)
            x_max = hist.get_hist().FindLastBinAbove(0)
            if x_min < x_min_use: x_min_use = x_min
            if x_max > x_max_use: x_max_use = x_max
            # find highest value along y axis
            current_height = hist.get_hist().GetMaximum()
            if current_height > maximum_height:
                maximum_height = current_height
            hist.set_canvas(self.canvas)
            hist.draw(config_str + "same")
        if x_min_use - 1 > 0: x_min_use -= 1
        if x_max_use + 1 < hist.get_hist().GetNbinsX(): x_max_use += 1
        if remove_empty_ends:
            self._hist_list[0].get_hist().GetXaxis().SetRange(
                x_min_use, x_max_use)
        self._hist_list[0].get_hist().GetYaxis().SetRangeUser(
            0, maximum_height * 1.4)
        self.canvas.BuildLegend(legend_paras[0], legend_paras[1],
                                legend_paras[2], legend_paras[3], legend_title)
        self._hist_list[0].get_hist().SetTitle(self.collection_name)
        self.canvas.Update()

    def save(self,
             save_dir: Union[str, None] = None,
             save_file_name: str = None,
             save_format: str = 'png') -> None:
        if save_dir is None:
            save_dir = os.getcwd() + "/hist_cols"
        else:
            if not os.path.isabs(save_dir):
                save_dir = "./" + save_dir
        if save_file_name is None:
            save_file_name = self.collection_name
        if not os.path.exists(save_dir):
            print("save_dir:", save_dir)
            os.makedirs(save_dir)
        save_path = save_dir + "/" + save_file_name + "." + save_format
        self.canvas.SaveAs(save_path)


class TH1Tool(object):
    """ROOT TH1 class wrapper for easy handling.

  Note:
    Base class, do not use directly

  """
    def __init__(self,
                 name: str,
                 title: str,
                 nbin: int = 50,
                 xlow: float = -100,
                 xup: float = 100,
                 config: Union[str, Cfg_Dict] = {},
                 create_new_canvas: 'bool' = False,
                 canvas: 'TCanvas' = None) -> None:
        self._hist = None
        self.name = name
        self.title = title
        self.canvas = canvas
        if create_new_canvas:
            self.create_canvas()
        self.config = self.parse_config(config)
        self._config_applied = False

    def __deepcopy__(self, memo) -> "TH1Tool":
        cls = self.__class__
        retrun_obj = cls.__new__(cls)
        memo[id(self)] = retrun_obj
        for key, value in self.__dict__.items():
            if key == "_hist": setattr(retrun_obj, "_hist", self._hist.Clone())
            elif key == "canvas": setattr(retrun_obj, "canvas", None)
            else: setattr(retrun_obj, key, copy.deepcopy(value, memo))
        return retrun_obj

    def apply_config(self) -> None:
        """Applys config associate with TH1Tool object.
    
    Note:
      When Draw() function called, if self._config_applied is False.
      This function will be called automatically before make plot.

    """
        config = self.config
        for section in config:
            if section == 'hist':
                config_hist = config['hist']
                self.apply_config_hist(config_hist)
            elif section == 'x_axis':
                config_x_axis = config['x_axis']
                self.apply_config_x_axis(config_x_axis)
            elif section == 'y_axis':
                config_y_axis = config['y_axis']
                self.apply_config_y_axis(config_y_axis)
            else:
                ValueError(
                    "Unsupported config section. Please change your config or add support."
                )
        self._config_applied = True

    def apply_config_hist(self, config: Cfg_Dict) -> None:
        """Applys general hist config."""
        for item in config:
            self.apply_single_config(self._hist, "hist", item)

    def apply_config_axis(self, axis: ROOT.TAxis, axis_section: str,
                          config: Cfg_Dict) -> None:
        """Applys axis config."""
        for item in config:
            self.apply_single_config(axis, axis_section, item)

    def apply_config_x_axis(self, config: Cfg_Dict) -> None:
        """Applys x axis config."""
        x_axis = self._hist.GetXaxis()
        self.apply_config_axis(x_axis, 'x_axis', config)

    def apply_config_y_axis(self, config: Cfg_Dict) -> None:
        """Applys y axis config."""
        y_axis = self._hist.GetYaxis()
        self.apply_config_axis(y_axis, 'y_axis', config)

    def apply_single_config(self, apply_object: Union[ROOT.TH1, ROOT.TAxis],
                            section_name: str, config_name: str) -> None:
        """Applys single config with mutable quantity inputs."""
        config_value = self.config[section_name][config_name]
        if type(config_value) is list:
            num_config_value = len(config_value)
        else:
            num_config_value = 1
        try:
            if num_config_value == 1:
                getattr(apply_object, config_name)(config_value)
            elif num_config_value == 2:
                getattr(apply_object, config_name)(config_value[0],
                                                   config_value[1])
            elif num_config_value == 3:
                getattr(apply_object,
                        config_name)(config_value[0], config_value[1],
                                     config_value[2])
            elif num_config_value == 4:
                getattr(apply_object,
                        config_name)(config_value[0], config_value[1],
                                     config_value[2], config_value[3])
            elif num_config_value == 5:
                getattr(apply_object,
                        config_name)(config_value[0], config_value[1],
                                     config_value[2], config_value[3],
                                     config_value[4])
            elif num_config_value == 6:
                getattr(apply_object,
                        config_name)(config_value[0], config_value[1],
                                     config_value[2], config_value[3],
                                     config_value[4], config_value[5])
            else:
                ValueError("Invalid num_config_value.")
        except:
            ValueError("Failed setting for:", config_name)

    def fill_hist(self, fill_array, weight_array=None):
        if weight_array is None:
            for element in fill_array:
                self._hist.Fill(element)
        else:
            for element, weight in zip(fill_array, weight_array):
                self._hist.Fill(element, weight)

    def create_canvas(self) -> None:
        self.canvas = ROOT.TCanvas(self.name + "_th1", self.title + "_th1",
                                   1600, 1000)

    def draw(self, config_str: str = None) -> None:
        """Makes the plot.
    
    Note:
      If self._config_appolied is False, self.apply_config() will be called.
    
    """
        if self.canvas is not None:
            self.canvas.cd()
        else:
            self.create_canvas()
        if not self._config_applied:
            self.apply_config()
        if config_str is not None:
            self._hist.Draw(config_str)
        else:
            self._hist.Draw()
        self.canvas.Update()

    def get_config(self) -> Cfg_Dict:
        return self.config

    def get_hist(self) -> ROOT.TH1:
        return self._hist

    def parse_config(self, config: Union[str, Cfg_Dict]) -> Cfg_Dict:
        """Reads json config.
    
    Note:
      If input is string (config file path), the config file will be open and
      json config will be read.
      If input is Cfg_Dict already, function will return a deep copy of input.
    
    """
        if type(config) is dict:
            return copy.deepcopy(config)
        elif type(config) is str:
            with open(config) as plot_config_file:
                return json.load(plot_config_file)
        else:
            ValueError("Unsupported config input type.")

    def save(self,
             save_dir: Union[str, None] = None,
             save_file_name: Union[str, None] = None,
             save_format: [str] = 'png') -> None:
        """Saves plots to specified path."""
        if save_dir is None:
            save_dir = "./hists"
        else:
            if not os.path.isabs(save_dir):
                save_dir = "./" + save_dir
        if save_file_name is None:
            save_file_name = self.name
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_path = save_dir + "/" + save_file_name + "." + save_format
        self.canvas.SaveAs(save_path)

    def set_canvas(self, canvas: ROOT.TCanvas) -> None:
        self.canvas = canvas

    def set_config(self, config: Cfg_Dict) -> None:
        self.config.update(self.parse_config(config))
        self._config_applied = False

    def set_hist(self, hist: ROOT.TH1) -> None:
        """Sets hist using external histogram."""
        self._hist = hist

    def update_config(self, section: str, item: str,
                      value: Union[str, int, float, list]) -> None:
        """Updates certain configuration.

    Note:
      If item existed, value will be updated to new value.
      If item doesn't exist, value will be created with new value.
    
    """
        section_value = {}
        try:
            section_value = self.config[section]
        except:
            pass
        section_value.update({item: value})
        self.config.update({section: section_value})
        self._config_applied = False


class TH1DTool(TH1Tool):
    """ROOT TH1D class wrapper for easy handling."""
    def __init__(self,
                 name: str,
                 title: str,
                 nbin: int = 50,
                 xlow: float = -100,
                 xup: float = 100,
                 config: Cfg_Dict = {},
                 create_new_canvas: bool = False,
                 canvas: Union[ROOT.TCanvas, None] = None) -> None:
        TH1Tool.__init__(self,
                         name,
                         title,
                         nbin=nbin,
                         xlow=xlow,
                         xup=xup,
                         config=config,
                         create_new_canvas=create_new_canvas,
                         canvas=canvas)
        self._hist = ROOT.TH1D(name, title, nbin, xlow, xup)


class TH1FTool(TH1Tool):
    """ROOT TH1F class wrapper for easy handling."""
    def __init__(self,
                 name: str,
                 title: str,
                 nbin: int = 50,
                 xlow: float = -100,
                 xup: float = 100,
                 config: Cfg_Dict = {},
                 create_new_canvas: bool = False,
                 canvas: Union[ROOT.TCanvas, None] = None) -> None:
        TH1Tool.__init__(self,
                         name,
                         title,
                         nbin=nbin,
                         xlow=xlow,
                         xup=xup,
                         config=config,
                         create_new_canvas=create_new_canvas,
                         canvas=canvas)
        self._hist = ROOT.TH1F(name, title, nbin, xlow, xup)
