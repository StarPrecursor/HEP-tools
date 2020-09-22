#!/usr/bin/env python
import ConfigParser
import glob
import sys
from array import array

import ROOT
from plot_helpers import *

ROOT.gROOT.SetBatch(ROOT.kTRUE)


def plot_brazilian(plot_config):
    """Makes Brazilian plots"""
    input_dict = process_input(plot_config)
    set_style(plot_config)

    num_points = input_dict["num_limits"]
    median_line = ROOT.TGraph(num_points)  # median line
    # for band plot, half point for upper bound and half for lower bound
    band_1sig = ROOT.TGraph(2 * num_points)  # green band
    band_2sig = ROOT.TGraph(2 * num_points)  # yellow band
    observed_line = ROOT.TGraph(num_points)  # median line

    # set curve and band
    combined_limits = input_dict["combined_limits"]
    for i in range(num_points):
        # median
        median_line.SetPoint(i, input_dict["x_points"][i], combined_limits[0][i])
        # + 1 sigma
        band_1sig.SetPoint(i, input_dict["x_points"][i], combined_limits[1][i])
        # + 2 sigma
        band_2sig.SetPoint(i, input_dict["x_points"][i], combined_limits[2][i])
        # - 1 sigma
        band_1sig.SetPoint(
            2 * num_points - 1 - i, input_dict["x_points"][i], combined_limits[3][i]
        )
        # - 2 sigma
        band_2sig.SetPoint(
            2 * num_points - 1 - i, input_dict["x_points"][i], combined_limits[4][i]
        )
        # observed
        observed_line.SetPoint(i, input_dict["x_points"][i], combined_limits[5][i])

    # plot ratio limit
    width = parse_int(plot_config, "PLOT", "canvas_width")
    height = parse_int(plot_config, "PLOT", "canvas_height")
    if width and height:
        plot_canvas = ROOT.TCanvas("c", "c", 100, 100, width, height)
    elif (not width) and (not height):
        plot_canvas = ROOT.TCanvas("c", "c", 100, 100, 600, 600)
    else:
        logging.warning(
            "You only specified width or height for the canvas, please check your settings. Using default (600, 600) this time."
        )
        plot_canvas = ROOT.TCanvas("c", "c", 100, 100, 600, 600)
    frame = plot_canvas.DrawFrame(1.4, 0.001, 4.1, 10)
    frame.GetXaxis().SetTitle(plot_config.get("PLOT", "x_title"))
    frame.GetYaxis().SetTitle(plot_config.get("PLOT", "y_title"))
    y_min = parse_float(plot_config, "PLOT", "y_min")
    if y_min:
        frame.SetMinimum(y_min)
    y_max = parse_float(plot_config, "PLOT", "y_max")
    if y_max:
        frame.SetMaximum(y_max)
    else:
        frame.SetMaximum(max(input_dict["upper_limits_plus2"]) * 1.05)
    frame.GetXaxis().SetLimits(min(input_dict["x_points"]), max(input_dict["x_points"]))

    band_2sig.SetFillColor(ROOT.kYellow)
    band_2sig.SetLineColor(ROOT.kYellow)
    band_2sig.SetFillStyle(1001)
    band_2sig.Draw("F")
    band_1sig.SetFillColor(ROOT.kGreen)
    band_1sig.SetLineColor(ROOT.kGreen)
    band_1sig.SetFillStyle(1001)
    band_1sig.Draw("F same")
    median_line.SetLineColor(1)
    median_line.SetLineWidth(2)
    median_line.SetLineStyle(2)
    median_line.Draw("L same")
    if parse_float_list(plot_config, "INPUT", "upper_limits_observed"):
        observed_line.SetLineColor(ROOT.kRed)
        observed_line.SetLineWidth(2)
        observed_line.Draw("L same")

    ROOT.gPad.SetTicks(1, 1)
    frame.Draw("sameaxis")
    if parse_bool(plot_config, "PLOT", "log_x"):
        plot_canvas.SetLogx()
    if parse_bool(plot_config, "PLOT", "log_y"):
        plot_canvas.SetLogy()

    save_folder = plot_config.get("FILE", "save_folder")
    if not save_folder:
        save_folder = "./"
    save_file = plot_config.get("FILE", "save_file")
    if not save_file:
        save_file = "UpperLimit"
    save_format = parse_str_list(plot_config, "FILE", "save_format")
    if not save_format:
        save_format = ["png"]
    for cur_format in save_format:
        plot_canvas.SaveAs(save_folder + "/" + save_file + "." + cur_format)
    plot_canvas.Close()


def set_style(plot_config):
    """Set styles for plotting
    
    Availabe styles:
        Classic(default), Plain, Bold, Video, Pub, Modern, ATLAS BELLE2
    
    """
    use_style = plot_config.get("PLOT", "style")
    if use_style:
        ROOT.gROOT.SetStyle(use_style)
    else:
        logging.warning("No style specified!")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        logging.critical("Missing config file!")
        exit()
    plot_config = ConfigParser.ConfigParser()
    plot_config.read(sys.argv[1])

    plot_brazilian(plot_config)
