import re
import random

import logging
from helpers.init_logging import init_logging

from .base_converter import convert_airplane_lights
from .converter_helpers import remove_flashing_sequences

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def convert_airbus_strobe_lights(animation: str, strobe_light_params_dict: dict[str, str]) -> str:
    """ Randomizes the ferquency for strobe lights so that not all
        aircraft flash at the same time

     Args:
         animation (str): The animations sequence with the strobe lights
         strobe_light_params_dict (dict[str, str]): The params for the strobe lights

     Returns:
             str: The updated animation with random strobe light frequency
    """
    light_type = "airplane_strobe"

    airbus_sequence_1: str = """
        ANIM_hide    0.0 0.10   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.15 0.25   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.30 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_2: str = """
        ANIM_hide    0.0 0.40   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.45 0.55   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.60 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_3: str = """
        ANIM_hide    0.0 0.70   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.75 0.85   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.90 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_4: str = """
        ANIM_hide    0.0 1.00   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.05 1.15   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.20 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_5: str = """
        ANIM_hide    0.0 1.15   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.20 1.30   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.35 1.5   sim/time/total_running_time_sec
    """

    flash_sequences = [
        airbus_sequence_1,
        airbus_sequence_2,
        airbus_sequence_3,
        airbus_sequence_4,
        airbus_sequence_5
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

    original_strobe_anim_hide = re.findall(
        "ANIM_hide.+libxplanemp/controls/strobe_lites_on", new_animation)

    if original_strobe_anim_hide == []:
        return animation

    new_animation = new_animation.replace(
        original_strobe_anim_hide[0], new_anim_hide)

    new_animation = new_animation.replace(
        "airplane_strobe", "airplane_generic")

    return new_animation
