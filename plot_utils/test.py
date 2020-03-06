import json

from ROOT import TH1F
from ROOT import kBlue

from plot_utils import *
from th1_tools import *

with open("test_plot_config.json") as plot_config_file:
  config=json.load(plot_config_file)
#### debug ####
print(json.dumps(config))

#test_canvas=ROOT.TCanvas("test canvas", "test canvas")

h1 = TH1FTool("h1", "test gaus", nbin=40, xlow=-5, xup=5)
h1.set_config(config)
h1.update_config('hist', 'SetLineColor', 2)
h1.apply_config()
#h1.draw()

h2 = TH1FTool("h2", "test gaus2", nbin=40, xlow=-5, xup=5)
h2.set_config(config)
h2.update_config('hist', 'SetLineColor', 7)
h2.apply_config()
#h2.draw("same")

#test_canvas.BuildLegend(0.75, 0.75, 0.9, 0.9, "test legend")  #
  # BuildLegend (Double_t x1=0.3, Double_t y1=0.21, Double_t x2=0.3, 
  # Double_t y2=0.21, const char *title="", Option_t *option="")
#test_canvas.Update()

hist_col = HistCollection([h1, h2])
hist_col.draw()

# stop exit
input("Press any key to exit.")
