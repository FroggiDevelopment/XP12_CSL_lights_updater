import os
import re

import logging
from helpers.init_logging import init_logging

from .converter_helpers import reduce_spill_intensity
from .converter_helpers import get_light_position
from .converter_helpers import get_leading_whitespaces
from .converter_helpers import remove_show_animation

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def remove_flashing_sequences(animation: str, light_type: str) -> str:
    pattern = r"(?s)(ANIM_hide.+sim/time/total_running_time_sec.+?ANIM_keyframe_loop \d.\d)"
    matches = re.findall(pattern, animation, re.MULTILINE)

    _light_name = light_type.split("_")[1]
    if matches != []:
        animation = animation.replace("generic", _light_name)
        for match in matches:
            animation = animation.replace(
                match, f"ANIM_hide -1.000000 0.000000 libxplanemp/controls/{_light_name}_lites_on")

    return animation


def convert_airplane_lights(animation: str, light_params_dict: dict[str, str], light_type: str) -> str:
    """ Basic conversion of airplane lights, result will be handled different from the 'calling' converters

    Args:
        animation (str): The animations sequence with the XP11 lights
        light_params_dict (dict[str, str]): The params for the XP12 lights

    Returns:
            str: The updated animations sequence with XP12 lights
    """
    _known_coordinates: list[str] = []
    _positions = ["_left", "_right", "_tail"]
    _light_name = light_type.split("_")[1]

    anim_frame: str = """
# New animation created by lights_updater for tail lights
ANIM_begin
    ANIM_hide    -1.0    0    libxplanemp/controls/@light_name@_lites_on
    @placeholder@
ANIM_end
    """

    # tabs to spaces
    animation.replace("\t", "    ")

    # remove flashing sequences if present (create clean base to comnvert)
    if "sim/time/total_running_time_sec" in animation:
        animation = remove_flashing_sequences(animation, light_type)

    # remove spill line extension so the new one(s) don't get delete in the process
    animation = animation.replace("_pm", "")

    # remove ANIM_show line if present as it is not needed
    animation = remove_show_animation(animation)

    list_of_animation_lines: list[str] = animation.splitlines()
    for line in list_of_animation_lines:
        light_position: str = ""

        if light_type in line:
            if "_size" in line:  # Maybe this will avoid some weird lights # TODO: To be tested more in detail later!
                animation = animation.replace(line, "")
                continue
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
            if re.search(r"\d+", line):
                new_line = line.replace("#", "")
            else:
                continue

            if light_type in ["airplane_nav", "airplane_strobe"]:
                light_position = get_light_position(line)

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
                    new_tail_line = f"    {tail_billboard_line}{os.linesep}        {tail_spill_line}"  # noqa
                    new_tail_line = new_tail_line.replace("_tail", "")

                    new_anim_frame = anim_frame.replace(
                        "@placeholder@", new_tail_line).replace("@light_name@", _light_name)

                    animation = animation+f"{os.linesep}"+new_anim_frame

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
            new_line = f"{leading_whitespaces}{billboard_line}{os.linesep}{leading_whitespaces}{spill_line}"
            animation = animation.replace(line, new_line)

    # remove empty lines
    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line.strip() != ""])

    return new_animation
