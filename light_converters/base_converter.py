import os
from .converter_helpers import reduce_spill_intensity
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
    animation.replace("\t", "....")

    # cleanup already converted lines
    # Remove _bb if already converted to ensure redo is possible
    animation = animation.replace("_bb", "")

    for line in animation.splitlines():
        if light_type in line:
            coordinates = f"{line.split()[2]}    {line.split()[3]}    {line.split()[4]}"
            if coordinates in _known_coordinates:
                animation = animation.replace(line, "")
                continue

            leading_whitespaces: str = get_leading_whitespaces(line)
            line_start = f"LIGHT_PARAM    {light_type}_bb"
            line_end = f"{light_params_dict[light_type]}"

            new_line = f"{line_start}   {coordinates}   {line_end}"
            spill_line = new_line.replace("_bb", "_pm")
            spill_line = reduce_spill_intensity(
                spill_line, light_type)

            new_line = f"{leading_whitespaces}{new_line}\n{leading_whitespaces}{spill_line}"

            _known_coordinates.append(coordinates)
            # print("##################### old line #####################")
            # print(line)
            # print("##################### new line #####################")
            # print(new_line)
            # print("###################################################")
            animation = animation.replace(line, new_line)
            # print(f"Manipulating round {counter}")
            # counter += 1
    # print("manipulated original animation")
    # print(animation)

    # remove empty lines
    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    # print("-----------CREATED ANIMATION--------------------------------")
    # print(new_animation)
    # print("-----------------------------------------------------------")
    return new_animation
