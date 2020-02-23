import json

import ROOT


class hist_collection(object):
  """Collection of histograms."""

  def __init__(
    self:'hist_collection',
    hist_list:'list',
    collection_name:'str'='hist collection',
    collection_title:'str'='hist collection',
    create_new_canvas:'bool'=False,
    canvas:'TCanvas'=None
    ) -> None:
    self.canvas=canvas
    self.collection_name = collection_name
    self.collection_title = collection_title
    self.hist_list = hist_list

    if type(hist_list) is not list:
      ValueError("Invalid hist_list type.")
    if len(hist_list) < 1:
      ValueError("Empty hist_list.")
    if create_new_canvas or (canvas is None):
      self.create_canvas()

  
  def create_canvas(
    self:'hist_collection',
    ) -> None:
    self.canvas=ROOT.TCanvas(self.collection_name, self.collection_title)

  
  def draw(
    self:'hist_collection',
    config_str:'str'="",
    legend_title:'str'="legend title"
    ) -> None:
    self.canvas.cd()
    maximum_height = -1e10
    for hist in self.hist_list:
      if hist.hist.GetMaximum() > maximum_height:
        maximum_height = hist.hist.GetMaximum()
      hist.set_canvas(self.canvas)
      hist.draw("same")
    self.hist_list[0].hist.GetYaxis().SetRangeUser(0, maximum_height*1.2)
    self.canvas.BuildLegend(0.7, 0.75, 0.9, 0.9, legend_title)
    self.canvas.Update()

class th1(object):
  """ROOT TH1 class wrapper for easy handling.
  
  Note:
    Base class, do not use directly
  
  """

  def __init__(
    self:'th1',
    name:'str',
    title:'str',
    nbin:'int'=50,
    xlow:'float'=-100,
    xup:'float'=100,
    config:'dict'={},
    create_new_canvas:'bool'=False,
    canvas:'TCanvas'=None
    ) -> None:

    self.hist=None
    self.name=name
    self.title=title

    self.canvas=canvas
    if create_new_canvas:
      self.create_canvas()
    self.config=config


  def apply_config(
    self:'th1'
    ) -> None:
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
      # debug test config
      elif section == 'test':
        print("#### DEBUG JSON ####")
        config_test = config['test']
        print(json.dumps(config_test))


  def apply_config_hist(
    self:'th1',
    config:'dict'
    ) -> None:
    """Applys general hist config."""
    for item in config:
      self.apply_single_config(self.hist, "hist", item)


  def apply_config_axis(
    self:'th1',
    axis:'TAxis',
    axis_section:'str',
    config:'dict'
    ) -> None:
    """Applys axis config."""
    for item in config:
      self.apply_single_config(axis, axis_section, item)


  def apply_config_x_axis(
    self:'th1',
    config:'dict'
    ) -> None:
    """Applys x axis config."""
    x_axis = self.hist.GetXaxis()
    self.apply_config_axis(x_axis, 'x_axis', config)


  def apply_config_y_axis(
    self:'th1',
    config:'dict'
    ) -> None:
    """Applys y axis config."""
    y_axis = self.hist.GetYaxis()
    self.apply_config_axis(y_axis, 'y_axis', config)

  
  def apply_single_config(
    self:'th1',
    apply_object:'object',
    section_name:'str',
    config_name:'str'
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
      elif num_config_value ==2:
        getattr(apply_object, config_name)(config_value[0], config_value[1])
      elif num_config_value ==3:
        getattr(apply_object, config_name)(
          config_value[0], config_value[1], config_value[2]
        )
      else:
        ValueError("Invalid num_config_value.")
    except:
      ValueError("Failed setting for:", config_name)


  def create_canvas(
    self:'th1',
    ) -> None:
    self.canvas=ROOT.TCanvas(self.name, self.title)


  def draw(
    self:'th1',
    config_str:'str'=None
    ) -> None:
    if self.canvas is not None:
      self.canvas.cd()
    else:
      self.create_canvas()
    if config_str is not None:
      self.hist.Draw(config_str)
    else:
      self.hist.Draw()
    self.canvas.Update()

  
  def get_config(
    self:'th1'
    ) -> 'dict':
    return self.config


  def set_canvas(
    self:'th1',
    canvas:'TCanvas'
    ) -> None:
    self.canvas = canvas

  
  def set_config(
    self:'th1',
    config:'dict'
    ) -> None:
    self.config = config


  def update_config(
    self:'th1',
    section:'str',
    item:'str',
    value:'str/int/float/list'
    ) -> None:
    """Updates certain configuration.

    Note:
      If item existed, value will be updated to new value.
      If item doesn't exist, value will be created with new value.
    
    """
    section_value = self.config[section]
    section_value.update({item:value})
    self.config.update({section: section_value})

class th1f(th1):
  """ROOT TH1F class wrapper for easy handling."""

  def __init__(
    self:'th1',
    name:'str',
    title:'str',
    nbin:'int'=50,
    xlow:'float'=-100,
    xup:'float'=100,
    config:'dict'={},
    create_new_canvas:'bool'=False,
    canvas:'TCanvas'=None
    ) -> None:
    th1.__init__(self, name, title, nbin=nbin, xlow=xlow, xup=xup,
      config=config, create_new_canvas=create_new_canvas, canvas=canvas)
    self.hist=ROOT.TH1F(name, title, nbin, xlow, xup)
