import re
import json


def reduce_spill_intensity(line: str, light_type: str) -> str:
    """Reduces the groundspill intensity of a light

    Args:
        line (str): A string with light specific parameters
        strength (float): A factor to reduce the intensity by.

    Returns:
        str: A line with reduced intensity
    """

    # get reduce factors from file
    with open("configs/aircraft_data.json", "r") as aircraft_data:
        aircraft_data = json.load(aircraft_data)
        reduce_factors = aircraft_data["reduce_factors"]

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


def increase_flashing_beacon_light_intensity(animation: str) -> str:
    """ Increase the candelar for the beacon if they are flashing

    Args:
        animation (str): The animations sequence with the beacons

    Returns:
            str: The updated animations sequence with increased candelar intensity for beacon lights
        """
    increase_beacon_intensity_factor: float = 2.0

    light_intensity_list: list[str] = re.findall(
        r"\d+cd", animation.lower())

    unique_light_intensity_list: list[str] = []

    [unique_light_intensity_list.append(
        val) for val in light_intensity_list if val not in unique_light_intensity_list]

    for light_intensity in unique_light_intensity_list:
        original_candelar = float(light_intensity.replace("cd", ""))
        increased_candelar = original_candelar * increase_beacon_intensity_factor
        new_light_intensity = f"{int(increased_candelar)}cd"
        animation = animation.replace(
            light_intensity, new_light_intensity)
    return animation
