#!/usr/bin/env python
import ConfigParser
import glob
import sys
import logging
from array import array

import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)


def parse_bool(plot_config, section, option):
    if plot_config.has_option(section, option):
        value = plot_config.get(section, option)
        if value:
            return plot_config.getboolean(section, option)
    return None


def parse_float(plot_config, section, option):
    if plot_config.has_option(section, option):
        value = plot_config.get(section, option)
        if value:
            return float(value)
    return None


def parse_float_list(plot_config, section, option):
    if plot_config.has_option(section, option):
        value = plot_config.get(section, option)
        if value:
            return [float(item.strip()) for item in value.split(",")]
    return []


def parse_int(plot_config, section, option):
    if plot_config.has_option(section, option):
        value = plot_config.get(section, option)
        if value:
            return int(value)
    return None


def parse_str_list(plot_config, section, option):
    if plot_config.has_option(section, option):
        value = plot_config.get(section, option)
        if value:
            return [item.strip() for item in value.split(",")]
    return []


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


def process_input(plot_config):
    """Checks & gets input numbers"""
    input_dict = {}
    x_points = parse_float_list(plot_config, "INPUT", "x_points")
    if not x_points:
        logging.critical("No x_points provided!")
        exit()
    else:
        input_dict["x_points"] = x_points
    input_dict["num_limits"] = len(x_points)
    input_dict["combined_limits"] = []

    # shouldn't change order of process, otherwise combined_limits will be wrong
    process_input_member(plot_config, "upper_limits_medium", input_dict)
    process_input_member(plot_config, "upper_limits_plus1", input_dict)
    process_input_member(plot_config, "upper_limits_plus2", input_dict)
    process_input_member(plot_config, "upper_limits_minus1", input_dict)
    process_input_member(plot_config, "upper_limits_minus2", input_dict)
    process_input_member(plot_config, "upper_limits_observed", input_dict)
    process_input_member(plot_config, "cross_sections", input_dict)

    combined_input = []
    if "upper_limits_medium" in input_dict:
        combined_input.append(input_dict["upper_limits_medium"])
    if "upper_limits_medium" in input_dict:
        combined_input.append(input_dict["upper_limits_medium"])
    else:
        combined_input.append(input_dict["upper_limits_medium"])

    return input_dict


def process_input_member(plot_config, input_name, input_dict):
    """Check whether the quantity of x_points and processed input member is consisted"""
    if "x_points" not in input_dict:
        logging.critical("Please process x_points first!")
        exit()
    else:
        num_limits = input_dict["num_limits"]
    input_member = parse_float_list(plot_config, "INPUT", input_name)
    if not input_member:
        logging.warning("No {} provided, will not include!".format(input_name))
        input_dict["combined_limits"].append(input_dict["upper_limits_medium"])
    else:
        input_dict[input_name] = input_member
        input_dict["combined_limits"].append(input_dict[input_name])
        if len(input_member) != num_limits:
            logging.error(
                "Quantity of {} is not consistent with x_points, please check!".format(
                    input_name
                )
            )
            exit()


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
