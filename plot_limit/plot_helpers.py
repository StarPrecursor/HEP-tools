import logging


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

