import re
import random
from .base_converter import convert_airplane_lights


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
        ANIM_hide    0.0 0.1   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.2 0.3   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.4 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_2: str = """
        ANIM_hide    0.0 0.4   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.6 0.7   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.9 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_3: str = """
        ANIM_hide    0.0 0.7   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    0.8 0.9   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.0 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_4: str = """
        ANIM_hide    0.0 1.0   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.1 1.2   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.3 1.5   sim/time/total_running_time_sec
    """

    airbus_sequence_5: str = """
        ANIM_hide    0.0 1.1   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.2 1.3   sim/time/total_running_time_sec
        ANIM_keyframe_loop 1.5
        ANIM_hide    1.4 1.5   sim/time/total_running_time_sec
    """

    flash_sequences = [
        airbus_sequence_1,
        airbus_sequence_2,
        airbus_sequence_3,
        airbus_sequence_4,
        airbus_sequence_5
    ]

    flash_sequence: str = random.choice(flash_sequences)

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
