import os
from .converter_helpers import reduce_spill_intensity
from .converter_helpers import get_light_position
from .converter_helpers import get_leading_whitespaces


def convert_airplane_lights(animation: str, light_params_dict: dict[str, str], light_type: str) -> str:
    """ Converts airplane lights

    Args:
        animation (str): The animations sequence with the XP11 lights
        light_params_dict (dict[str, str]): The params for the XP12 lights

    Returns:
            str: The updated animations sequence with XP12 lights
    """
    _known_coordinates: list[str] = []
    _positions = ["_left", "_right", "_tail"]

    # tabs to spaces
    animation.replace("\t", "    ")

    # remove spill line extension so the new one(s) don't get delete in the process
    animation = animation.replace("_pm", "")

    list_of_animation_lines: list[str] = animation.splitlines()
    for line in list_of_animation_lines:
        light_position: str = ""
        if light_type in line:

            coordinates = f"{line.split()[2]}    {line.split()[3]}    {line.split()[4]}"
            if coordinates in _known_coordinates:
                animation = animation.replace(line, "")
                continue
            else:
                _known_coordinates.append(coordinates)

            leading_whitespaces = get_leading_whitespaces(line)
            new_line = line.replace("#", "")

            if light_type in ["airplane_nav"]:
                light_position = get_light_position(new_line)
                new_line = new_line.replace(
                    f"{light_type}", f"{light_type}{light_position}")
                light_type = f"{light_type}{light_position}"

            line_start = f"LIGHT_PARAM    {light_type}_bb"
            line_end = f"{light_params_dict[light_type]}"

            # Remove positional arguments from the line
            if any((position := positional_argument) in line_start for positional_argument in _positions):
                line_start = line_start.replace(position, "")
                light_type = light_type.replace(position, "")

            billboard_line = f"{line_start}   {coordinates}   {line_end}"
            spill_line = billboard_line.replace("_bb", "_pm")
            spill_line = reduce_spill_intensity(
                spill_line, light_type)
            new_line = f"{leading_whitespaces}{billboard_line}\n{leading_whitespaces}{spill_line}"
            animation = animation.replace(line, new_line)

    # remove empty lines
    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line.strip() != ""])

    return new_animation
