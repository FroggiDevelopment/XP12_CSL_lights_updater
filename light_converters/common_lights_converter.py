# import os
import re

import logging
from helpers.init_logging import init_logging

from .converter_helpers import reduce_spill_intensity
from .converter_helpers import get_nav_light_position
from .converter_helpers import get_strobe_light_positions
from .converter_helpers import get_leading_whitespaces
from .converter_helpers import remove_show_animation

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def convert_airplane_lights(animation: str, light_params_dict: dict[str, str], light_type: str) -> str:
    """ Basic conversion of airplane lights, result will be handled different from the 'calling' converters

    Args:
        animation (str): The animations sequence with the XP11 lights
        light_params_dict (dict[str, str]): The params for the XP12 lights

    Returns:
            str: The updated animations sequence with XP12 lights
    """
    _known_coordinates: list[str] = []
    _positions = ["_left", "_right", "_tail", "_lower", "_upper"]
    _light_name = light_type.split("_")[1]
    _illegal_lights: list[str] = ["headlight", "airplane_beacon_rotate_sp"]

    anim_frame: str = """
# New animation created for tail lights by lights_updater
ANIM_begin
    ANIM_hide    -1.0    0    libxplanemp/controls/@light_name@_lites_on
    @placeholder@
ANIM_end
    """

    # Convert to new naming convention
    animation = animation.replace("LIGHT_NAMED", "LIGHT_PARAM")

    # tabs to spaces
    animation.replace("\t", "    ")

    # remove spill line extension so the new one(s) don't get delete in the process
    animation = animation.replace("_pm", "")

    # remove ANIM_show line if present as it is not needed
    animation = remove_show_animation(animation)

    list_of_animation_lines: list[str] = animation.splitlines()

    for line in list_of_animation_lines:
        # Remove illegal lights that are not supported in XP12
        if any(illegal_light in line for illegal_light in _illegal_lights):
            animation = animation.replace(line, "")
            continue

        light_position: str = ""

        if light_type in line:
            # Uncomment only lines with digits. They should be light param lines.
            if re.search(r"\d+", line):
                new_line = line.replace("#", "")
            else:
                continue
            if "_size" in line:  # Maybe this will avoid some weird lights # TODO: To be tested more in detail later!
                animation = animation.replace(line, "")
                continue
            # Seems some artistic way to comment unwanted lines. Found in some obj files. Drop it! :-)
            if "#~" in line:
                animation = animation.replace(line, "")
                continue

            coordinates = f"{line.split()[2]}    {line.split()[3]}    {line.split()[4]}"

            if coordinates in _known_coordinates:
                animation = animation.replace(line, "")
                log.debug(
                    f"{light_type} at {coordinates} already converted, skipping this one!")
                continue
            else:
                _known_coordinates.append(coordinates)

            leading_whitespaces = get_leading_whitespaces(line)

            # TODO: Rewrite base converter to get rid of specific converter related code!!! If possible!?
            if light_type in ["airplane_nav", "airplane_strobe"]:
                # TODO: Send positional arguments to the specific converters
                if light_type == "airplane_strobe":
                    light_position = get_strobe_light_positions(line)
                else:
                    light_position = get_nav_light_position(line)

                new_line = new_line.replace(
                    f"{light_type}", f"{light_type}{light_position}")
                # TODO: Can this be moved to the specific converters??
                if "_tail" in line:
                    new_anim_frame = anim_frame
                    animation = animation.replace(line, "")

                    tail_billboard_line = f"LIGHT_PARAM airplane_nav_tail_bb {coordinates} {light_params_dict['airplane_nav_tail']}"  # noqa
                    tail_spill_line = tail_billboard_line.replace("_bb", "_pm")

                    tail_spill_line = reduce_spill_intensity(
                        tail_spill_line, "airplane_nav")
                    new_tail_line = f"    {tail_billboard_line}\n        {tail_spill_line}"  # noqa
                    new_tail_line = new_tail_line.replace("_tail", "")

                    new_anim_frame = anim_frame.replace(
                        "@placeholder@", new_tail_line).replace("@light_name@", _light_name)

                    animation = animation+"\n"+new_anim_frame

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
    new_animation = "\n".join(
        [line for line in animation.splitlines() if line.strip() != ""])

    return new_animation
