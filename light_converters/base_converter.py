import os
from helpers.light_manipulators import reduce_spill_intensity
from helpers.light_manipulators import get_leading_whitespaces


def convert_airplane_lights(animation: str, light_params_dict: dict[str, str], light_type: str) -> str:
    """ Converts airplane lights

    Args:
        animation (str): The animations sequence with the XP11 lights
        light_params_dict (dict[str, str]): The params for the XP12 lights

    Returns:
            str: The updated animations sequence with XP12 lights
    """
    _known_coordinates: list[str] = []
    animation.replace("\t", "....")

    for line in animation.splitlines():
        if light_type in line:
            leading_whitespaces: str = get_leading_whitespaces(line)
            coordinates = f"{line.split()[2]}    {line.split()[3]}    {line.split()[4]}"
            if coordinates in _known_coordinates:
                animation = animation.replace(line, "")
                continue
            _known_coordinates.append(coordinates)
            line_start = f"LIGHT_PARAM    {light_type}_bb"
            line_end = f"{light_params_dict[light_type]}"

            new_line = f"{line_start}   {coordinates}   {line_end}"
            spill_line = new_line.replace("_bb", "_pm")
            spill_line = reduce_spill_intensity(
                spill_line, light_type)

            new_line = f"{leading_whitespaces}{new_line}\n{leading_whitespaces}{spill_line}"

            animation = animation.replace(line, new_line)

    # remove empty lines
    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    return new_animation
