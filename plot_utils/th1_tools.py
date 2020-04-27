import copy
import json
import math
import os
import warnings
from typing import Dict, List, Union

import ROOT
from HEPTools.plot_utils import plot_utils

Cfg_Dict = Dict[str, Union[int, float, str, Dict[str, Union[int, float, str]]]]


class HistCollection(object):
    """Collection of histograms.

    A class to handle ROOT histograms collection plotting easily. 

    """

    def __init__(
            self,
            hist_list: List["TH1Tool"],
            name: str = 'hist collection',
            title: str = 'hist collection',
            create_new_canvas: bool = False,
            canvas: Union[ROOT.TCanvas, None] = None) -> None:
        """Inits HistCollection with a list of TH1Tool objects."""
        self._canvas = canvas
        self._name = name
        self._title = title
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
        """Creats new canvas for drawing."""
        self._canvas = ROOT.TCanvas(self._name + "_col", self._title + "_col",
                                    800, 600)

    def draw(
            self,
            draw_options: str = "",
            legend_title: str = "legend title",
            legend_paras: list = [0.75, 0.75, 0.9, 0.9],
            draw_norm: bool = False,
            remove_empty_ends: bool = False,
            norm_factor: float = 1.) -> None:
        """Plots HistCollection on canvas.

        Args:

            draw_options: Options applied when calling draw function in ROOT.
            legend_title: Title to be displayed in plot legend.
            legend_paras: List to define the legend location, length must be 4.
                From 1st to last elements: x1, x2, y1, y2 (corresponding to the
                ratio of the plot pad)
            draw_norm: Whether to draw normalized plot.
            remove_empty_ends: Whether to remove leading/trailing empty bins.
            norm_factor: If draw_norm is True, histograms will be normalized to 
                this value.

        """
        self._canvas.cd()
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
            if x_min < x_min_use:
                x_min_use = x_min
            if x_max > x_max_use:
                x_max_use = x_max
            # find highest value along y axis
            current_height = hist.get_hist().GetMaximum()
            if current_height > maximum_height:
                maximum_height = current_height
            hist.set_canvas(self._canvas)
            hist.draw(draw_options + "same")
        if x_min_use - 1 > 0:
            x_min_use -= 1
        if x_max_use + 1 < hist.get_hist().GetNbinsX():
            x_max_use += 1
        if remove_empty_ends:
            self._hist_list[0].get_hist().GetXaxis().SetRange(
                x_min_use, x_max_use)
        self._hist_list[0].get_hist().GetYaxis().SetRangeUser(
            0, maximum_height * 1.4)
        self._canvas.BuildLegend(legend_paras[0], legend_paras[1],
                                 legend_paras[2], legend_paras[3],
                                 legend_title)
        self._hist_list[0].get_hist().SetTitle(self._name)
        self._canvas.Update()

    def save(
            self,
            save_dir: Union[str, None] = None,
            save_file_name: str = None,
            save_format: str = 'png') -> None:
        """Saves the plot on canvas to file.

        The plot will be saved to 'save_dir/save_file_name.save_format'.

        """
        if save_dir is None:
            save_dir = os.getcwd() + "/hist_cols"
        else:
            if not os.path.isabs(save_dir):
                save_dir = "./" + save_dir
        if save_file_name is None:
            save_file_name = self._name
        if not os.path.exists(save_dir):
            print("save_dir:", save_dir)
            os.makedirs(save_dir)
        save_path = save_dir + "/" + save_file_name + "." + save_format
        self._canvas.SaveAs(save_path)


class RatioPlot(object):
    """Ratio plot object.

    A class for easy ratio plot drawing on TPad/TCanvas.

    """

    def __init__(
            self,
            hist_numerator: "TH1Tool",
            hist_denominator: "TH1Tool",
            name: str = "hist ratio",
            title: str = "hist ratio",
            x_title: str = "var",
            y_title: str = "data/bkg",
            create_new_canvas: bool = False,
            canvas: Union[ROOT.TCanvas, None] = None) -> None:
        """Inits RatioPlot with numerator/denominator histograms."""
        self._canvas = canvas
        self.name = name
        self.title = title
        self.x_title = x_title
        self.y_title = y_title
        self._hist_numerator = copy.deepcopy(hist_numerator)
        self._hist_denominator = copy.deepcopy(hist_denominator)
        self._hist_ratio = copy.deepcopy(hist_numerator)
        self._hist_ratio.get_hist().Divide(self._hist_denominator.get_hist())
        self._hist_ratio_err = copy.deepcopy(hist_denominator)
        self._hist_ratio_err.get_hist().Divide(self._hist_denominator.get_hist())
        if create_new_canvas or (canvas is None):
            self.create_canvas()
        self.style_cfg = {
            "hist": {
                "SetDefaultSumw2": True,
                "SetMinimum": 0.5,
                "SetMaximum": 1.5,
                "SetStats": 0,
                "SetTitle": "",
                "SetFillColor": ROOT.kGray
            },
            "x_axis": {
                "SetTitle": self.x_title,
                "SetTitleSize": 20,
                "SetTitleFont": 43,
                "SetTitleOffset": 4.,
                "SetLabelFont": 43,
                "SetLabelSize": 15
            },
            "y_axis": {
                "SetTitle": self.y_title,
                "SetNdivisions": 505,
                "SetTitleSize": 0.04,
                "SetTitleFont": 43,
                "SetTitleOffset": 1,
                "SetLabelFont": 43,
                "SetLabelSize": 15
            }
        }

    def create_canvas(self) -> None:
        """Creats new canvas for drawing."""
        self._canvas = ROOT.TCanvas(
            self.name + "_ratio", self.title + "_ratio", 800, 600)

    def draw(
        self,
        draw_options: str = "e3"
    ):
        """Plots HistCollection on canvas.

        Args:

            draw_options: Options applied when calling draw function in ROOT.

        """
        self._canvas.cd()
        # plot bkg error bar
        self._hist_ratio_err.set_config(self.style_cfg)
        self._hist_ratio_err.apply_config()
        self._hist_ratio_err.get_hist().Draw(draw_options)
        # plot base line
        base_line = ROOT.TF1("one", "1", 0, 1)
        base_line.SetLineColor(ROOT.kRed)
        base_line.Draw("same")
        # plot ratio
        self._hist_ratio.get_hist().Draw("same")


class TH1Tool(object):
    """ROOT TH1 class wrapper for easy handling.

    Note:
        Base class, do not use directly

    """

    def __init__(
            self,
            name: str,
            title: str,
            nbin: int = 50,
            xlow: float = -100,
            xup: float = 100,
            config: Union[str, Cfg_Dict] = {},
            create_new_canvas: 'bool' = False,
            canvas: 'TCanvas' = None,
            canvas_id: int = 1) -> None:
        """Inits TH1Tool.

        Note:
            canvas_id starts from 1

        Cfgs:
            config: configurations and operations for plotting. example:
            {
                "hist": {
                    "SetDefaultSumw2": True,
                    "SetStats": 0,
                    "SetFillColor": ROOT.kGray
                },
                "x_axis": {
                    "SetTitle": self.x_title
                },
                "y_axis": {
                    "SetTitle": self.y_title
                }
            }

        """
        self._hist = None
        self.name = name
        self.title = title
        self._canvas = canvas
        self._canvas_id = canvas_id
        if create_new_canvas:
            self.create_canvas()
        self.config = self.parse_config(config)
        self._config_applied = False

    def __deepcopy__(self, memo) -> "TH1Tool":
        cls = self.__class__
        retrun_obj = cls.__new__(cls)
        memo[id(self)] = retrun_obj
        for key, value in self.__dict__.items():
            if key == "_hist":
                setattr(retrun_obj, "_hist", self._hist.Clone())
            elif key == "canvas":
                setattr(retrun_obj, "canvas", None)
            else:
                setattr(retrun_obj, key, copy.deepcopy(value, memo))
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

    def apply_single_config(
            self,
            apply_object: Union[ROOT.TH1, ROOT.TAxis],
            section_name: str,
            config_name: str) -> None:
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

    def build_legend(
            self,
            x1: float = 0.8,
            y1: float = 0.75,
            x2: float = 0.9,
            y2: float = 0.9) -> None:
        """Build legend on the canvas.

        Cfgs:
            (x1, y1) means bottom-left point (ratio) of the rectangular.
            (x2, y2) means top-right point (ratio) of the rectangular.

        """
        self._canvas.BuildLegend(x1, y1, x2, y2)
        self._canvas.Update()

    def create_canvas(self) -> None:
        """Creats new canvas for drawing."""
        self._canvas = ROOT.TCanvas(self.name + "_th1", self.title + "_th1",
                                    800, 600)
        self._canvas_id = 0

    def draw(self, draw_options: str = "", log_scale=False) -> None:
        """Makes the plot.

        Note:
            If self._config_appolied is False, self.apply_config() will be called.

        Args:
            draw_options: Options applied when calling draw function in ROOT.

        """
        # make sure weight is correct
        self.get_hist().SetDefaultSumw2()
        # make plot
        if self._canvas is None:
            self.create_canvas()
        self._canvas.cd(self._canvas_id)
        if not self._config_applied:
            self.apply_config()
        if log_scale:
            self._canvas.SetLogy(2)
        self._hist.Draw(draw_options)
        self._canvas.Update()

    def fill_hist(self, fill_array, weight_array=None):
        """Fills the histogram with array."""
        if weight_array is None:
            for element in fill_array:
                self._hist.Fill(element)
        else:
            for element, weight in zip(fill_array, weight_array):
                self._hist.Fill(element, weight)

    def get_canvas(self) -> ROOT.TCanvas:
        """Returns the ROOT canvas in use."""
        return self._canvas

    def get_config(self) -> Cfg_Dict:
        """Returns the histogram config."""
        return self.config

    def get_hist(self) -> ROOT.TH1:
        """Returns the ROOT TH1 object."""
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

    def save(
            self,
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
        self._canvas.SaveAs(save_path)

    def set_canvas(self, canvas: ROOT.TCanvas) -> None:
        """Sets canvas from external."""
        self._canvas = canvas

    def set_config(self, config: Cfg_Dict) -> None:
        """Sets hisogram configurations."""
        self.config.update(self.parse_config(config))
        self._config_applied = False

    def set_hist(self, hist: ROOT.TH1) -> None:
        """Sets hist using external histogram."""
        self._hist = hist

    def update_config(
            self, section: str,
            item: str,
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

    def __init__(
            self,
            name: str,
            title: str,
            nbin: int = 50,
            xlow: float = -100,
            xup: float = 100,
            config: Cfg_Dict = {},
            create_new_canvas: bool = False,
            canvas: Union[ROOT.TCanvas, None] = None,
            canvas_id: int = 1) -> None:
        """Inits TH1DTool"""
        super().__init__(
            name,
            title,
            nbin=nbin,
            xlow=xlow,
            xup=xup,
            config=config,
            create_new_canvas=create_new_canvas,
            canvas=canvas,
            canvas_id=canvas_id)
        self._hist = ROOT.TH1D(name, title, nbin, xlow, xup)
        self.nbin = nbin
        self.xlow = xlow
        self.xup = xup

    def reinitial_hist_with_fill_array(self, fill_array):
        """Reset histogram with new bin range with given fill array."""
        xlow = math.floor(min(fill_array))
        xup = math.ceil(max(fill_array))
        self._hist = ROOT.TH1D(self.name, self.title, self.nbin, xlow, xup)


class TH1FTool(TH1Tool):
    """ROOT TH1F class wrapper for easy handling."""

    def __init__(
            self,
            name: str,
            title: str,
            nbin: int = 50,
            xlow: float = -100,
            xup: float = 100,
            config: Cfg_Dict = {},
            create_new_canvas: bool = False,
            canvas: Union[ROOT.TCanvas, None] = None,
            canvas_id: int = 1) -> None:
        """Inits TH1FTool"""
        super().__init__(
            name,
            title,
            nbin=nbin,
            xlow=xlow,
            xup=xup,
            config=config,
            create_new_canvas=create_new_canvas,
            canvas=canvas,
            canvas_id=canvas_id)
        self._hist = ROOT.TH1F(name, title, nbin, xlow, xup)
        self.nbin = nbin
        self.xlow = xlow
        self.xup = xup

    def reinitial_hist_with_fill_array(self, fill_array):
        """Reset histogram with new bin range with given fill array."""
        xlow = math.floor(min(fill_array))
        xup = math.ceil(max(fill_array))
        self._hist = ROOT.TH1F(self.name, self.title, self.nbin, xlow, xup)


class THStackTool(object):
    """ROOT THStack class wrapper for easy handing"""

    def __init__(
            self,
            name: str,
            title: str,
            hist_list: List["TH1Tool"],
            create_new_canvas: bool = False,
            canvas: Union[ROOT.TCanvas, None] = None) -> None:
        """Inits THStackTool."""
        super().__init__()
        self.name = name
        self.title = title
        self._hist_list = []
        for hist in hist_list:
            self._hist_list.append(copy.deepcopy(hist))
        self.create_new_canvas = create_new_canvas
        self._canvas = canvas
        if create_new_canvas or (canvas is None):
            self.create_canvas()
        self._hist_stack = ROOT.THStack(name, title)
        for hist in self._hist_list:
            self._hist_stack.Add(hist.get_hist())

    def build_legend(
            self,
            x1: float = 0.8,
            y1: float = 0.75,
            x2: float = 0.9,
            y2: float = 0.9) -> None:
        """Build legend on the canvas.

        Cfgs:
            (x1, y1) means bottom-left point (ratio) of the rectangular.
            (x2, y2) means top-right point (ratio) of the rectangular.

        """
        self._canvas.BuildLegend(x1, y1, x2, y2)
        self._canvas.Update()

    def create_canvas(self) -> None:
        """Creats new canvas for drawing."""
        self._canvas = ROOT.TCanvas(self.name + "_stack",
                                    self.title + "_stack", 800, 600)

    def draw(self, draw_cfg="", log_scale=False):
        """Makes the plot.

        Args:
            draw_options: Options applied when calling draw function in ROOT.

        """
        ROOT.gStyle.SetPalette(ROOT.kPastel)
        self._canvas.cd()
        if log_scale:
            self._canvas.SetLogy(2)
        self._hist_stack.Draw(draw_cfg)
        self._canvas.Update()

    def get_added_hist(self) -> ROOT.TH1:
        """Combines hists in self._hist_list together."""
        merged_hist_root = plot_utils.merge_hists(self._hist_list)
        merged_hist = TH1Tool("merged_hist", "merged_hist")
        merged_hist._hist = merged_hist_root
        return merged_hist

    def get_canvas(self) -> ROOT.TCanvas:
        """Returns the ROOT canvas in use."""
        return self._canvas

    def get_hist_list(self) -> list:
        """Returns a list of TH1Tool in self._hist_list"""
        return self._hist_list

    def get_hstack(self) -> ROOT.THStack:
        """Returns ROOT hist stack object."""
        return self._hist_stack

    def get_total_weights(self) -> float:
        """Returns sum of SumOfWeights of all histograms in self._hist_list"""
        total_weights = 0
        for hist in self._hist_list:
            total_weights += hist.get_hist().GetSumOfWeights()
        return total_weights

    def save(
            self,
            save_dir: Union[str, None] = None,
            save_file_name: str = None,
            save_format: str = 'png') -> None:
        """Saves plots to specified path."""
        if save_dir is None:
            save_dir = os.getcwd() + "/hist_stacks"
        else:
            if not os.path.isabs(save_dir):
                save_dir = "./" + save_dir
        if save_file_name is None:
            save_file_name = self.name
        if not os.path.exists(save_dir):
            print("save_dir:", save_dir)
            os.makedirs(save_dir)
        save_path = save_dir + "/" + save_file_name + "." + save_format
        self._canvas.SaveAs(save_path)

    def set_canvas(self, canvas: ROOT.TCanvas) -> None:
        """Sets canvas from external."""
        self._canvas = canvas
