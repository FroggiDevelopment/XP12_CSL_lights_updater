import re


def reduce_spill_intensity(line: str, light_type: str) -> str:
    """Reduces the groundspill intensity of a light

    Args:
        line (str): A string with light specific parameters
        strength (float): A factor to reduce the intensity by.

    Returns:
        str: A line with reduced intensity
    """
    reduce_factors: dict[str, float] = {
        "airplane_landing": 1.00,
        "airplane_taxi": 0.75,
        "airplane_nav": 0.40,
        "airplane_beacon": 0.35,
        "airplane_strobe": 0.50
    }

    current_candelar = re.search(r"\d+cd", line)

    if current_candelar:
        raw_candelar_value = current_candelar.group(0).replace("cd", "")

        reduced_candelar = int(float(raw_candelar_value)
                               * reduce_factors[light_type])

        new_intensity_line = line.replace(
            current_candelar.group(0), f"{str(reduced_candelar)}cd")

        return new_intensity_line
    return line


def get_leading_whitespaces(line: str) -> str:
    """ Get leading whitespaces from line to ensure identation is kept
        This is for the readability of the obj files themself

    Args:
        line_with_light_information (str): The line with the light information

    Returns:
        str: leading whitespaces
    """
    leading_whitespaces = re.match(r"^\s*", line)

    if leading_whitespaces is None:
        return ""
    return leading_whitespaces.group()


def add_lateral_position_to_lights(line: str) -> str:
    """To determine directional parameters add left, right or tail to the light param
       based on x-y-position of the light.
       Will be removed again later on in the process.

    Args:
        line (str): Line with light-parameters.

    Returns:
        str: Line with 'positional' light-name-parameters. I.e. airplane_nav_rigt
    """
    # If the line already includes position, return it unprocessed.
    if any(position in line for position in ["left", "right", "tail"]):
        return line

    _x_position = float(line.split()[2:3][0])
    actual_lighttype = line.split()[1]

    if (_x_position) > -0.50 and _x_position < 0.50:
        lighttype = f"{actual_lighttype}_tail"
    elif (_x_position) < -0.50:
        lighttype = f"{actual_lighttype}_left"
    else:
        lighttype = f"{actual_lighttype}_right"

    return line.replace(actual_lighttype, lighttype)


def get_light_position(line: str) -> str:
    """To determine directional parameters return _left, _right or _tail based on
       x-y-position of the light.
       Will be removed again later on in the process.

    Args:
        line (str): Line with light-parameters.

    Returns:
        str: postion of the light
    """
    position: str = ""

    _x_position = float(line.split()[2:3][0])

    if (_x_position) > -0.50 and _x_position < 0.50:
        position = "_tail"
    elif (_x_position) < -0.50:
        position = "_left"
    else:
        position = "_right"

    return position
