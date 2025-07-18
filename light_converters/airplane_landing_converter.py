import re
import os

import logging
from helpers.init_logging import init_logging

from .base_converter import convert_airplane_lights
from .converter_helpers import get_leading_whitespaces

import configs.aircraft_processing_data as aircraft_processing_data

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def convert_airplane_landing_lights(animation: str, light_params_dict: dict[str, str]) -> str:
    """ Converts airplane lights

    Args:
        animation (str): The animations sequence with the XP11 lights
        light_params_dict (dict[str, str]): The params for the XP12 lights

    Returns:
            str: The updated animations sequence with XP12 lights
    """

    # Get rid of illegal lights in landig lights animation
    if "airplane_landing" not in animation:
        log.error("Found illegal light in animation! Removing this light animation")
        return ""

    light_type = "airplane_landing"

    new_animation = convert_airplane_lights(
        animation, light_params_dict, light_type)

    if "libxplanemp/controls/gear_ratio" not in animation:
        new_animation = fix_frontgear_landinglights(new_animation)
    return new_animation


def fix_frontgear_landinglights(animation: str) -> str:
    """Fixes the case where the frontgear landinglights were still visible after the landing gear is retracted

    Args:
        animation (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str | None: Fixed textblock, None if nothing has changed
    """
    light_parameter: list[str] = re.findall(
        r"LIGHT_PARAM\s+airplane_landing.+", animation)

    if light_parameter == []:
        log.error(
            f"{__name__} - No light parameter found in file: {aircraft_processing_data.AircraftData.full_object_path}")
        return animation

    log.debug("Fixing frontgear landinglights hide animation.")

    extra_anim_hide: str = (
        "ANIM_hide -1.000000 0.800000 libxplanemp/controls/gear_ratio"
    )

    original_landinglight_anim_show: re.Match[str] | None = re.search(
        r"ANIM_show.+landing_lites_on", animation
    )

    if original_landinglight_anim_show:
        landinglight_anim_show = original_landinglight_anim_show.group()
        animation = animation.replace(
            landinglight_anim_show,
            "",
        )

    original_landinglight_anim_hide: re.Match[str] | None = re.search(
        r"ANIM_hide.+libxplanemp/controls/landing_lites_on", animation
    )
    if original_landinglight_anim_hide:
        landinglight_anim_hide = original_landinglight_anim_hide.group()
        leading_whitespaces = get_leading_whitespaces(
            landinglight_anim_hide).replace("\n", "")

        x_position = float(light_parameter[0].split()[2])

        if x_position < 0.4 and x_position > -0.4:
            new_animation = animation.replace(
                landinglight_anim_hide,
                f"{leading_whitespaces}{landinglight_anim_hide}{os.linesep}{leading_whitespaces}{extra_anim_hide}",
            )

            # remove empty lines
            new_animation = os.linesep.join(
                [line for line in new_animation.splitlines() if line.strip() != ""])

            return new_animation

    return animation
