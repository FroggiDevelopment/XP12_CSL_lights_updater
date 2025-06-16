import re
import os
import random

import logging
from helpers.init_logging import init_logging

from .base_converter import convert_airplane_lights
from .converter_helpers import increase_flashing_beacon_light_intensity

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def convert_airplane_beacon_lights(animation: str, light_params_dict: dict[str, str]) -> str:
    light_type = "airplane_beacon"

    new_animation = convert_airplane_lights(
        animation, light_params_dict, light_type)

    return new_animation


def convert_airplane_flashing_beacon_lights(animation: str, beacon_light_params_dict: dict[str, str]) -> str:
    """ Converts airplane beacon lights to flashing beacons

     Args:
         animation (str): The animations sequence with the beacon lights
         beacon_light_params_dict (dict[str, str]): The beacon light parameters

     Returns:
             str: The updated animations sequence with flashing beacon lights
     """
    new_animation = convert_airplane_beacon_lights(
        animation, beacon_light_params_dict)

    beacon_sequence_1 = """
        ANIM_hide    0.0 0.1   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.2 1.5   sim/time/total_running_time_sec
    """

    beacon_sequence_2 = """
        ANIM_hide    0.0 0.4   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.5 1.5   sim/time/total_running_time_sec
    """

    beacon_sequence_3 = """
        ANIM_hide    0.0 0.7   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.8 1.5   sim/time/total_running_time_sec
    """

    beacon_sequence_4 = """
        ANIM_hide    0.0 1.0   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.1 1.5   sim/time/total_running_time_sec
    """

    beacon_sequence_5 = """
        ANIM_hide    0.0 1.3   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.4 1.5   sim/time/total_running_time_sec
    """

    flash_sequences: list[str] = [
        beacon_sequence_1,
        beacon_sequence_2,
        beacon_sequence_3,
        beacon_sequence_4,
        beacon_sequence_5
    ]
    # get flashing sequence
    flash_sequence = random.choice(flash_sequences)

    pattern = r"(?s)(ANIM_hide.+sim/time/total_running_time_sec.+?ANIM_keyframe_loop \d.\d)"
    matches = re.findall(pattern, new_animation, re.MULTILINE)

    # remove previous flashing sequence
    for match in matches:
        new_animation = new_animation.replace(
            match, "ANIM_hide	-1.0 0.0	libxplanemp/controls/beacon_lites_on")

    new_anim_hide = f"""
    ANIM_hide	-1.0 0.0	libxplanemp/controls/beacon_lites_on
    {flash_sequence}
    ANIM_keyframe_loop 1.5
    """

    original_beacon_anim_hide = re.findall(
        "ANIM_hide.+libxplanemp/controls/beacon_lites_on", new_animation)

    if original_beacon_anim_hide != []:
        new_animation = new_animation.replace(
            original_beacon_anim_hide[0], new_anim_hide)

    new_animation = new_animation.replace(
        "airplane_beacon", "airplane_generic")

    new_animation = increase_flashing_beacon_light_intensity(new_animation)

    # remove empty lines
    new_animation = os.linesep.join(
        [line for line in new_animation.splitlines() if line.strip() != ""])
    return new_animation
