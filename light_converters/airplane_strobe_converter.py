import re
# import os
import random

import logging
from helpers.init_logging import init_logging

from .common_lights_converter import convert_airplane_lights
from .converter_helpers import remove_flashing_sequences

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def convert_airplane_strobe_lights(animation: str, strobe_light_params_dict: dict[str, str]) -> str:
    """ Converts strobe lights tp XP 12 standrad and randomizes the frequency for strobe lights,
        so that not all aircraft flash at the same time

     Args:
         animation (str): The animations sequence with the strobe lights
         strobe_light_params_dict (dict[str, str]): The params for the strobe lights

     Returns:
             str: The updated animation with random strobe light frequency
    """
    light_type = "airplane_strobe"

    flash_sequence_1: str = """
        ANIM_hide    0.0 0.10   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.15 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_2: str = """
        ANIM_hide    0.0 0.20   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.25 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_3: str = """
        ANIM_hide    0.0 0.30   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.35 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_4: str = """
        ANIM_hide    0.0 0.40   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.45 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_5: str = """
        ANIM_hide    0.0 0.50  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.55 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_6: str = """
        ANIM_hide    0.0 0.60  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.65 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_7: str = """
        ANIM_hide    0.0 0.70  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.75 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_8: str = """
        ANIM_hide    0.0 0.80  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.85 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_9: str = """
        ANIM_hide    0.0 0.90  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.95 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_10: str = """
        ANIM_hide    0.0 1.00  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.05 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_11: str = """
        ANIM_hide    0.0 1.10  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.15 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_12: str = """
        ANIM_hide    0.0 1.20  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.25 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_13: str = """
        ANIM_hide    0.0 1.30  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.35 1.5   sim/time/total_running_time_sec
    """

    flash_sequence_14: str = """
        ANIM_hide    0.0 1.40  sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.45 1.5   sim/time/total_running_time_sec
    """

    flash_sequences: list[str] = [flash_sequence_1,
                                  flash_sequence_2,
                                  flash_sequence_3,
                                  flash_sequence_4,
                                  flash_sequence_5,
                                  flash_sequence_6,
                                  flash_sequence_7,
                                  flash_sequence_8,
                                  flash_sequence_9,
                                  flash_sequence_10,
                                  flash_sequence_11,
                                  flash_sequence_12,
                                  flash_sequence_13,
                                  flash_sequence_14
                                  ]

    flash_sequence: str = random.choice(flash_sequences)

    # Remove prior flashing sequenece if present
    if "sim/time/total_running_time_sec" in animation:
        animation = remove_flashing_sequences(animation, light_type)

    new_anim_hide = f"""
    ANIM_hide    -1.0    0    libxplanemp/controls/strobe_lites_on
    {flash_sequence}
    ANIM_keyframe_loop 1.5
    """

    new_animation = convert_airplane_lights(
        animation, strobe_light_params_dict, light_type)

    original_beacon_anim_hide = re.findall(
        "ANIM_hide.+libxplanemp/controls/strobe_lites_on", new_animation)

    if original_beacon_anim_hide == []:
        return animation

    new_animation = new_animation.replace(
        original_beacon_anim_hide[0], new_anim_hide)

    new_animation = new_animation.replace(
        "airplane_strobe", "airplane_generic")

    new_animation = "\n".join(
        [line for line in new_animation.splitlines() if line.strip() != ""])

    return new_animation
