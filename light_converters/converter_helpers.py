import re
import json

import logging
from helpers.init_logging import init_logging

# Setup logging
init_logging()
log = logging.getLogger(__name__)


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
    else:
        log.error(f"Found no candelar value in {line}")
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


def get_light_position(line: str) -> str:
    """To determine directional parameters return _left, _right or _tail based on
       x-y-position of the light.
       Will be removed again later on in the process.

    Args:
        line (str): Line with light-parameters.

    Returns:
        str: postion of the light
    """

    _x_position = float(line.split()[2:3][0])

    if (_x_position) > -0.50 and _x_position < 0.50:
        return "_tail"
    elif (_x_position) < -0.50:
        return "_left"

    return "_right"


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


def remove_show_animation(animation: str) -> str:
    """ Remove the show animation line (ANIM_show) from the animation

    Args:
        animation (str): The animations

    Returns:
            str: The updated animations without the show animation
        """

    original_anim_show: re.Match[str] | None = re.search(
        r"ANIM_show.+lites_on", animation
    )

    if original_anim_show:
        landinglight_anim_show = original_anim_show.group()
        animation = animation.replace(
            landinglight_anim_show,
            "",
        )

    return animation
