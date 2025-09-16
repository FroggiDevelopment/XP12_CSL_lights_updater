import re
import logging
from helpers import init_logging

from .common_lights_converter import convert_airplane_lights
from .converter_helpers import get_leading_whitespaces

# Setup logging
init_logging()
log = logging.getLogger("airplane_taxi_converter")


def convert_airplane_taxi_lights(animation: str, light_params_dict: dict[str, str]) -> str:
    light_type = "airplane_taxi"

    # For those cases that the taxi lights are in the wrong animation, corerect the dataref.
    if "libxplanemp/controls/landing_lites_on" in animation:
        animation = animation.replace("landing_lites_on", "taxi_lites_on")

    new_animation = convert_airplane_lights(
        animation, light_params_dict, light_type)

    # Add ANIM_hide animation to hide when rectracted
    if "libxplanemp/controls/gear_ratio" not in animation:
        new_animation = fix_taxilights(new_animation)
    return new_animation


def fix_taxilights(animation: str) -> str:
    """Fixes the wrong dataref for taxilights where applicable

    Args:
        animation (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str : Fixed textblock
    """
    log.debug("Fixing frontgear taxilights hide animation.")
    extra_anim_hide: str = (
        "ANIM_hide -1.000000 0.800000 libxplanemp/controls/gear_ratio"
    )
    new_animation = animation.replace("landing_lites_on", "taxi_lites_on")

    original_taxi_anim_hide: re.Match[str] | None = re.search(
        r"ANIM_hide.+libxplanemp/controls/taxi_lites_on", new_animation
    )
    if original_taxi_anim_hide:
        anim_hide_line = original_taxi_anim_hide.group()

        leading_whitespaces = get_leading_whitespaces(anim_hide_line)

        new_animation = new_animation.replace(
            original_taxi_anim_hide[0],
            f"{original_taxi_anim_hide[0]}\n{leading_whitespaces}{extra_anim_hide}",
        )
        original_taxi_anim_show = re.findall(
            "ANIM_show.+taxi_lites_on", new_animation)

        if original_taxi_anim_show != []:
            new_animation = new_animation.replace(
                f"{original_taxi_anim_show[0]}\n",
                "",
            )
        return new_animation
    log.error("Fixing frontgear taxilights hide animation failed.")
    return animation
