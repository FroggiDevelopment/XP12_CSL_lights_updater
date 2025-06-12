import os
import logging
from helpers import init_logging
from .converter_helpers import get_leading_whitespaces
from .converter_helpers import get_light_position
from .converter_helpers import reduce_spill_intensity

# Setup logging
init_logging()
log = logging.getLogger("airplane_nav_converter")


def convert_airplane_nav_lights(animation: str, light_params_dict: dict[str, str]) -> str:
    """ Converts airplane nav lights

    Args:
        animation (str): The animations sequence with the nav lights
        nav_light_params_dict (dict[str, str]): The params for the nav lights

    Returns:
            str: The updated animations sequence with nav lights
    """
    light_type: str = "airplane_nav"
    _known_coordinates: list[str] = []
    positions = ["_left", "_right", "_tail"]

    # Remove _bb and _pm if already converted to ensure redo is possible
    # animation = animation.replace("_bb", "")
    # animation = animation.replace("_pm", "")

    for line in animation.splitlines():
        light_position: str = ""
        new_line_start: str = f"LIGHT_PARAM   {light_type}"

        if light_type in line:
            # Check if light at this position is already converted
            coordinates = f"{line.split()[2]}    {line.split()[3]}    {line.split()[4]}"
            if coordinates in _known_coordinates:
                animation = animation.replace(line, "")
                continue

            leading_whitespaces = get_leading_whitespaces(line)
            # Remove possible comment sign
            new_line = line.replace("#", "")

            # Add positional argument to the line
            light_position: str = get_light_position(new_line)

            new_line_start = f"{new_line_start}{light_position}"

            light_key_string = f"{light_type}{light_position}"
            line_end = f"{light_params_dict[light_key_string]}"

            new_line = f"{new_line_start}   {coordinates}   {line_end}"

            # Remove positional arguments from the line
            if any((position := positional_argument) in new_line for positional_argument in positions):
                new_line = new_line.replace(position, "")

            new_line = new_line.replace(light_type, f"{light_type}_bb")

            spill_line = new_line.replace("_bb", "_pm")
            spill_line = reduce_spill_intensity(
                spill_line, light_type)

            new_line = f"{leading_whitespaces}{new_line}\n{leading_whitespaces}{spill_line}"

            _known_coordinates.append(coordinates)

            animation = animation.replace(line, new_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    return new_animation
