import copy
import os
from typing import Dict, List, Union
import json

import ROOT

Cfg_Dict = Dict[str, Union[int, float, str, Dict[str, Union[int, float, str]]]]

class hist_collection(object):
  """Collection of histograms."""

  def __init__(
    self,
    hist_list:List[ROOT.TH1],
    collection_name:str='hist collection',
    collection_title:str='hist collection',
    create_new_canvas:bool=False,
    canvas:Union[ROOT.TCanvas, None]=None
    ) -> None:
    self.canvas=canvas
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
    self.canvas=ROOT.TCanvas(
      self.collection_name, self.collection_title, 1600, 1000)


  def draw(
    self,
    config_str:str="",
    legend_title:str="legend title",
    draw_norm:bool=False,
    norm_factor:float=1.
    ) -> None:
    self.canvas.cd()
    maximum_height = -1e10
    for hist in self._hist_list:
      if draw_norm:
        total_weight = hist.get_hist().Integral("width")
        if total_weight != 0:
          hist.get_hist().Scale(1/total_weight)
      current_height = hist.get_hist().GetMaximum()
      if current_height > maximum_height:
        maximum_height = current_height
      hist.set_canvas(self.canvas)
      hist.draw(config_str + "same")
    self._hist_list[0].get_hist().GetYaxis().SetRangeUser(0, maximum_height*1.2)
    self.canvas.BuildLegend(0.75, 0.65, 0.9, 0.9, legend_title)
    self._hist_list[0].get_hist().SetTitle(self.collection_name)
    self.canvas.Update()


  def save(
    self,
    save_dir:Union[str, None]=None,
    save_file_name:str=None,
    save_format:str='png'
    ) -> None:
    if save_dir is None:
      save_dir = os.getcwd() + "/hists"
    if save_file_name is None:
      save_file_name = self.collection_name
    if not os.path.exists(save_dir):
      os.makedirs(save_dir)
    save_path = save_dir + "/" + save_file_name + "." + save_format
    self.canvas.SaveAs(save_path)

class th1(object):
  """ROOT TH1 class wrapper for easy handling.

  Note:
    Base class, do not use directly

  """

  _hist = None
  _config_applied = False

  def __init__(
    self,
    name:str,
    title:str,
    nbin:int=50,
    xlow:float=-100,
    xup:float=100,
    config:Union[str, Cfg_Dict]={},
    create_new_canvas:'bool'=False,
    canvas:'TCanvas'=None
    ) -> None:
    self._hist=None
    self.name=name
    self.title=title
    self.canvas=canvas
    if create_new_canvas:
      self.create_canvas()
    self.config = self.parse_config(config)


  def apply_config(self) -> None:
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
        ValueError("Unsupported config section. Please change your config or add support.")
    self._config_applied = True


  def apply_config_hist(self, config:Cfg_Dict) -> None:
    """Applys general hist config."""
    for item in config:
      self.apply_single_config(self._hist, "hist", item)


  def apply_config_axis(
    self,
    axis:ROOT.TAxis,
    axis_section:str,
    config:Cfg_Dict
    ) -> None:
    """Applys axis config."""
    for item in config:
      self.apply_single_config(axis, axis_section, item)


  def apply_config_x_axis(self, config:Cfg_Dict) -> None:
    """Applys x axis config."""
    x_axis = self._hist.GetXaxis()
    self.apply_config_axis(x_axis, 'x_axis', config)


  def apply_config_y_axis(self, config:Cfg_Dict) -> None:
    """Applys y axis config."""
    y_axis = self._hist.GetYaxis()
    self.apply_config_axis(y_axis, 'y_axis', config)


  def apply_single_config(
    self,
    apply_object:Union[ROOT.TH1, ROOT.TAxis],
    section_name:str,
    config_name:str
    ) -> None:
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
        getattr(apply_object, config_name)(config_value[0], config_value[1])
      elif num_config_value == 3:
        getattr(apply_object, config_name)(config_value[0], config_value[1],
                                           config_value[2])
      elif num_config_value == 4:
        getattr(apply_object, config_name)(config_value[0], config_value[1],
                                           config_value[2], config_value[3])
      elif num_config_value == 5:
        getattr(apply_object, config_name)(config_value[0], config_value[1],
          config_value[2], config_value[3], config_value[4])
      elif num_config_value == 6:
        getattr(apply_object, config_name)(config_value[0], config_value[1],
          config_value[2], config_value[3], config_value[4], config_value[5])
      else:
        ValueError("Invalid num_config_value.")
    except:
      ValueError("Failed setting for:", config_name)


  def create_canvas(self) -> None:
    self.canvas=ROOT.TCanvas(self.name, self.title)


  def draw(self, config_str:str=None) -> None:
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


  def parse_config(self, config:Union[str, Cfg_Dict]) -> Cfg_Dict:
    if type(config) is dict:
      return copy.deepcopy(config)
    elif type(config) is str:
      with open(config) as plot_config_file:
        return json.load(plot_config_file)
    else:
      ValueError("Unsupported config input type.")

  def save(
    self,
    save_dir:Union[str, None]=None,
    save_file_name:Union[str, None]=None,
    save_format:[str]='png'
    ) -> None:
    if save_dir is None:
      save_dir = os.getcwd() + "/hists"
    if save_file_name is None:
      save_file_name = self.name
    if not os.path.exists(save_dir):
      os.makedirs(save_dir)
    save_path = save_dir + "/" + save_file_name + "." + save_format
    self.canvas.SaveAs(save_path)


  def set_canvas(self, canvas:ROOT.TCanvas) -> None:
    self.canvas = canvas


  def set_config(self, config:Cfg_Dict) -> None:
    self.config = self.parse_config(config)
    self._config_applied = False


  def set_hist(self, hist:ROOT.TH1) -> None:
    """Sets hist using external histogram."""
    self._hist = hist


  def update_config(
    self,
    section:str,
    item:str,
    value:Union[str, int, float, list]
    ) -> None:
    """Updates certain configuration.

    Note:
      If item existed, value will be updated to new value.
      If item doesn't exist, value will be created with new value.
    
    """
    section_value = self.config[section]
    section_value.update({item:value})
    self.config.update({section: section_value})
    self._config_applied = False

class th1d(th1):
  """ROOT TH1D class wrapper for easy handling."""

  def __init__(
    self,
    name:str,
    title:str,
    nbin:int=50,
    xlow:float=-100,
    xup:float=100,
    config:Cfg_Dict={},
    create_new_canvas:bool=False,
    canvas:Union[ROOT.TCanvas, None]=None
    ) -> None:
    th1.__init__(self, name, title, nbin=nbin, xlow=xlow, xup=xup,
      config=config, create_new_canvas=create_new_canvas, canvas=canvas)
    self._hist=ROOT.TH1D(name, title, nbin, xlow, xup)

class th1f(th1):
  """ROOT TH1F class wrapper for easy handling."""

  def __init__(
    self,
    name:str,
    title:str,
    nbin:int=50,
    xlow:float=-100,
    xup:float=100,
    config:Cfg_Dict={},
    create_new_canvas:bool=False,
    canvas:Union[ROOT.TCanvas, None]=None
    ) -> None:
    th1.__init__(self, name, title, nbin=nbin, xlow=xlow, xup=xup,
      config=config, create_new_canvas=create_new_canvas, canvas=canvas)
    self._hist=ROOT.TH1F(name, title, nbin, xlow, xup)

def has_sub_string(
  check_string:str,
  sub_strings:Union[str, list]
  ) -> bool:
  if type(sub_strings) is list:
    for sub_string in sub_strings:
      if sub_string in check_string:
        return True
  elif type(sub_strings) is str:
    if sub_strings in check_string:
      return True
  return False