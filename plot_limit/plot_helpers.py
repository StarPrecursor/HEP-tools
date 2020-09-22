import logging

import ROOT

# atlas_* functions are adapted from ATLASUtil.py


def atlas_draw_ecm(x, y, ecm, color=1):
    atlas_draw_text(x, y, "#sqrt{s} = " + str(ecm) + " TeV", color, 0.035)
    return


def atlas_draw_luminosity(x, y, lumi, color=1):
    atlas_draw_text(x, y, "#intLdt = " + str(lumi) + " pb^{-1}", color, 0.05)
    return


def atlas_draw_luminosity_fb(x, y, lumi, energy, color=1):
    atlas_draw_text(x, y, str(energy) + " TeV, " + str(lumi) + " fb^{-1}", color, 0.035)
    return


def atlas_draw_text(
    x, y, text, color=1, size=0.04, NDC=True, halign="left", valign="bottom", angle=0.0
):
    objs = []
    skipLines = 0
    for line in text.split("\n"):
        objs.append(
            atlas_draw_text_one_line(
                x, y, line, color, size, NDC, halign, valign, skipLines, angle
            )
        )
        if NDC == True:
            y -= 0.05 * size / 0.04
        else:
            skipLines += 1
    return objs


def atlas_draw_text_one_line(
    x,
    y,
    text,
    color=1,
    size=0.04,
    NDC=True,
    halign="left",
    valign="bottom",
    skipLines=0,
    angle=0.0,
):
    halignMap = {"left": 1, "center": 2, "right": 3}
    valignMap = {"bottom": 1, "center": 2, "top": 3}
    scaleLineHeight = 1.0
    if valign == "top":
        scaleLineHeight = 0.8
    if skipLines:
        text = "#lower[%.1f]{%s}" % (skipLines * scaleLineHeight, text)
    # Draw the text quite simply:
    l = ROOT.TLatex()
    if NDC:
        l.SetNDC()
    l.SetTextAlign(10 * halignMap[halign] + valignMap[valign])
    l.SetTextColor(color)
    l.SetTextSize(size)
    l.SetTextAngle(angle)
    l.DrawLatex(x, y, text)
    return l


def atlas_label(x, y, color=1, plot_status="Internal"):
    l = ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextColor(color)
    l.DrawLatex(x, y, "ATLAS")
    l.SetTextFont(42)
    l.DrawLatex(x + 0.16, y, plot_status)
    return


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


def parse_str(plot_config, section, option):
    if plot_config.has_option(section, option):
        value = plot_config.get(section, option)
        value = value.strip(r"""'" """)
        if value:
            return value
    return None


def parse_str_list(plot_config, section, option):
    if plot_config.has_option(section, option):
        value = plot_config.get(section, option)
        if value:
            return [item.strip() for item in value.split(",")]
    return []


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
    input_dict["y_points_collect"] = []
    # check whether have TrexFitter input
    if parse_bool(plot_config, "TREX", "use_trex_input"):
        logging.info("Using limits input from TRexFitter...")
        path_prefix = parse_str(plot_config, "TREX", "path_prefix")
        path_suffix = parse_str(plot_config, "TREX", "path_suffix")
        tree_name = parse_str(plot_config, "TREX", "tree_name")
        folders = parse_str_list(plot_config, "TREX", "folders")
        medium_values = []
        plus1_values = []
        plus2_values = []
        minus1_values = []
        minus2_values = []
        obs_values = []
        for folder in folders:
            path = path_prefix + "/" + folder + "/" + path_suffix
            limit_file = ROOT.TFile.Open(path, "read")
            limit_tree = limit_file.Get(tree_name)
            for event in limit_tree:
                medium_values.append(event.exp_upperlimit)
                plus1_values.append(event.exp_upperlimit_plus1)
                plus2_values.append(event.exp_upperlimit_plus2)
                minus1_values.append(event.exp_upperlimit_minus1)
                minus2_values.append(event.exp_upperlimit_minus2)
                obs_values.append(event.obs_upperlimit)
                break  # only 1 entry
        process_input_member_trex("upper_limits_medium", medium_values, input_dict)
        process_input_member_trex("upper_limits_plus1", plus1_values, input_dict)
        process_input_member_trex("upper_limits_plus2", plus2_values, input_dict)
        process_input_member_trex("upper_limits_minus1", minus1_values, input_dict)
        process_input_member_trex("upper_limits_minus2", minus2_values, input_dict)
        process_input_member_trex("upper_limits_observed", obs_values, input_dict)
    else:
        logging.info("Using limits input from config...")
        # shouldn't change order of process, otherwise y_points_collect will be wrong
        process_input_member(plot_config, "upper_limits_medium", input_dict)
        process_input_member(plot_config, "upper_limits_plus1", input_dict)
        process_input_member(plot_config, "upper_limits_plus2", input_dict)
        process_input_member(plot_config, "upper_limits_minus1", input_dict)
        process_input_member(plot_config, "upper_limits_minus2", input_dict)
        process_input_member(plot_config, "upper_limits_observed", input_dict)
    process_input_member(plot_config, "cross_sections", input_dict)

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
        input_dict["y_points_collect"].append(input_dict["upper_limits_medium"])
    else:
        input_dict[input_name] = input_member
        input_dict["y_points_collect"].append(input_dict[input_name])
        if len(input_member) != num_limits:
            logging.error(
                "Quantity of {} is not consistent with x_points, please check!".format(
                    input_name
                )
            )
            exit()


def process_input_member_trex(input_name, input_values, input_dict):
    """Check whether the quantity of x_points and processed input member is consisted"""
    if "x_points" not in input_dict:
        logging.critical("Please process x_points first!")
        exit()
    else:
        num_limits = input_dict["num_limits"]
    if not input_values:
        logging.warning("No {} provided, will not include!".format(input_name))
        input_dict["y_points_collect"].append(input_dict["upper_limits_medium"])
    else:
        input_dict[input_name] = input_values
        input_dict["y_points_collect"].append(input_dict[input_name])
        if len(input_values) != num_limits:
            logging.error(
                "Quantity of {} is not consistent with x_points, please check!".format(
                    input_name
                )
            )
            exit()
